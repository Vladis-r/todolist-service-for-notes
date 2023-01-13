import typing
from typing import Optional, List

from django.core.management import BaseCommand
from django.db.models import QuerySet

from bot.management.commands import LINK_TO_GOAL
from bot.tg.client import TgClient
from todolist.settings import TG_TOKEN

from bot.models import TgUser
from bot.tg.dc import Message, SendMessageResponse
from goals.models import Goal, GoalCategory


class BotMessage:
    """
    Класс с сообщениями для бота
    """
    message_verify_code = "Подтвердите свой аккаунт на сайте с помощью кода: "
    message_lists_of_goal = "Список целей: "
    message_choose_category = "Выберите категорию: "
    message_choose_goal = "Введите желанную цель: "
    message_operation_canceled = "Операция отменена"
    message_unknown_category = "Не существует категории с таким названием"
    message_unknown_command = "Неизвестная команда"


class BotRunner(BotMessage):
    """
    Класс, отвечающий за общение с пользователем.
    Имеет 4 вида состояний (condition)
    """
    tg_user = None
    category: Optional[GoalCategory] = None
    condition: int = 0

    def __init__(self, msg: Message, tg_client: TgClient) -> None:
        self.msg = msg
        self.tg_client = tg_client

    def send_message(self, text: str, msg: Message) -> SendMessageResponse:
        """
        Функция для отправки сообщений пользователю
        """
        message = self.tg_client.send_message_to_url(
            chat_id=msg.chat.id,
            text=f"{text}"
        )
        return message

    def create_tg_user(self, msg: Message) -> tuple:
        """
        Создание пользователя в Телеграме (модель - TgUser)
        """
        BotRunner.tg_user, created = TgUser.objects.get_or_create(
            tg_user_id=msg.message_from.id,
            tg_chat_id=msg.chat.id
        )
        return BotRunner.tg_user, created

    def get_goals(self) -> typing.Union[QuerySet, List[Goal]]:
        """
        Функция для получения целей пользователя
        """
        try:
            result = Goal.objects.filter(
                category__board__participants__user=self.tg_user.user).exclude(status=Goal.Status.archived)
        except AttributeError:
            text = "Не создано ни одной цели"
            self.send_message(text=text, msg=self.msg)
            return []
        return result

    def get_categories(self) -> typing.Union[QuerySet, List[GoalCategory]]:
        """
        Функция для получения категорий пользователя
        """
        try:
            result = GoalCategory.objects.filter(
                board__participants__user=self.tg_user.user).exclude(is_deleted=True)
        except AttributeError:
            text = "Не создано ни одной категории"
            self.send_message(text=text, msg=self.msg)
            return []
        return result

    def start_bot(self) -> typing.Generator:
        """
        Основная функция с логикой работы бота
        """
        while BotRunner.condition == 0:
            BotRunner.tg_user, created = self.create_tg_user(self.msg)
            if not self.tg_user.user:
                code = self.tg_user.generate_verification_code()
                text = f"{self.message_verify_code} \n {code}"
                yield self.send_message(text=text, msg=self.msg)
            else:
                BotRunner.condition = 1

        while BotRunner.condition == 1:
            if self.msg.text == "/goals":
                self.send_goals(self.msg)
                yield
            if self.msg.text == "/create":
                self.send_categories(self.msg)
                BotRunner.condition = 2
                yield
            else:
                yield self.send_message(text=self.message_unknown_command, msg=self.msg)

        while BotRunner.condition == 2:
            if self.msg.text == "/cancel":
                self.send_message(text=self.message_operation_canceled, msg=self.msg)
                BotRunner.condition = 1
                yield
            elif self.get_categories().filter(title=self.msg.text):
                BotRunner.category = self.get_categories().filter(title=self.msg.text).first()
                self.send_message(text=self.message_choose_goal, msg=self.msg)
                BotRunner.condition = 3
                yield
            else:
                yield self.send_message(text=self.message_unknown_category, msg=self.msg)

        while BotRunner.condition == 3:
            if self.msg.text == "/cancel":
                self.send_message(text=self.message_operation_canceled, msg=self.msg)
                BotRunner.condition = 1
                yield
            else:
                self.create_goal(msg=self.msg, category=BotRunner.category)
                BotRunner.condition = 0
                yield

    def send_categories(self, msg: Message) -> None:
        """
        Функция для отправки категорий пользователю
        """
        if self.get_categories():
            categories_list = "\n".join(["- " + category.title for category in self.get_categories()])
            text = f"{self.message_choose_category} \n {categories_list}"
            self.send_message(text=text, msg=msg)
        else:
            self.send_message(text="Категорий нет", msg=self.msg)

    def send_goals(self, msg: Message) -> None:
        """
        Функция для отправки целей пользователю
        """
        if self.get_goals():
            goals_list = "\n".join(["- " + goal.title for goal in self.get_goals()])
            text = f"{self.message_lists_of_goal} \n {goals_list}"
            self.send_message(text=text, msg=msg)
        else:
            self.send_message(text="Целей нет", msg=self.msg)

    def create_goal(self, msg: Message, category: Optional[GoalCategory]) -> None:
        """
        Функция для создания новой цели с помощью Телеграма
        """
        goal = Goal.objects.create(title=msg.text,
                                   category=category,
                                   user=BotRunner.tg_user.user
                                   )
        text = f"Цель создана: \n{LINK_TO_GOAL}goals?goal={goal.id}"
        self.send_message(text=text, msg=msg)


class Command(BaseCommand):
    """
    Запускает работу бота (python manage.py runbot)
    """
    help = "run bot in Telegram"
    tg_client: TgClient = TgClient(TG_TOKEN)

    def handle(self, *args: typing.Any, **options: typing.Any) -> None:
        """
        Запускаем бота.
        Получаем обновления с Телеграма и передаём в BotRunner
        """
        offset: int = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                if hasattr(item, "message"):
                    bot_runner = BotRunner(msg=item.message, tg_client=self.tg_client)
                    next(bot_runner.start_bot())
