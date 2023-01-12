from django.core.management import BaseCommand

from bot.management.commands import LINK_TO_GOAL
from bot.tg.client import tg_client, TgClient
from todolist.settings import TG_TOKEN

from bot.models import TgUser
from bot.tg.dc import Message
from goals.models import Goal, Status, GoalCategory


class BotMessage:
    message_verify_code = "Подтвердите свой аккаунт на сайте с помощью кода: "
    message_lists_of_goal = "Список целей: "
    message_choose_category = "Выберите категорию: "
    message_choose_goal = "Введите желанную цель: "
    message_operation_canceled = "Операция отменена"
    message_unknown_category = "Не существует категории с таким названием"
    message_unknown_command = "Неизвестная команда"

    def send_message(self, text: str, msg: Message):
        message = tg_client.send_message_to_url(
            chat_id=msg.chat.id,
            text=f"{text}"
        )
        return message


class BotRunner(BotMessage):
    tg_user = None
    category = None
    condition = 0

    def __init__(self, msg: Message):
        self.msg = msg

    def create_tg_user(self, msg: Message):
        BotRunner.tg_user, created = TgUser.objects.get_or_create(
            tg_user_id=msg.message_from.id,
            tg_chat_id=msg.chat.id
        )
        return BotRunner.tg_user, created

    def get_goals(self):
        try:
            result = Goal.objects.filter(
                category__board__participants__user=self.tg_user.user).exclude(status=Status.archived)
        except AttributeError:
            text = "Не создано ни одной цели"
            self.send_message(text=text, msg=self.msg)
            return []
        return result

    def get_categories(self):
        try:
            result = GoalCategory.objects.filter(
                board__participants__user=self.tg_user.user).exclude(is_deleted=True)
        except AttributeError:
            text = "Не создано ни одной категории"
            self.send_message(text=text, msg=self.msg)
            return []
        return result

    def start_bot(self):
        print(f"кондиция бота: {BotRunner.condition}")
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
                yield self.send_goals(self.msg)
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

    def send_categories(self, msg: Message):
        if self.get_categories():
            categories_list = "\n".join(["- " + category.title for category in self.get_categories()])
            text = f"{self.message_choose_category} \n {categories_list}"
            self.send_message(text=text, msg=msg)
        else:
            self.send_message(text="Категорий нет", msg=self.msg)

    def send_goals(self, msg: Message):
        if self.get_goals():
            goals_list = "\n".join(["- " + goal.title for goal in self.get_goals()])
            text = f"{self.message_lists_of_goal} \n {goals_list}"
            self.send_message(text=text, msg=msg)
        else:
            self.send_message(text="Целей нет", msg=self.msg)

    def create_goal(self, msg: Message, category: str):
        goal = Goal.objects.create(title=msg.text,
                                   category=category,
                                   user=self.tg_user.user
                                   )
        text = f"Цель создана: \n{LINK_TO_GOAL}goals?goal={goal.id}"
        self.send_message(text=text, msg=msg)


class Command(BaseCommand):
    help = "run bot in Telegram"
    tg_client = TgClient(TG_TOKEN)

    def __init__(self):
        self.tg_client = tg_client
        super().__init__()

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                if hasattr(item, "message"):
                    bot_runner = BotRunner(msg=item.message)
                    next(bot_runner.start_bot())
