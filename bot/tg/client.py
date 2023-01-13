from typing import Optional

import requests

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse, GET_UPDATES_SCHEMA, SEND_MESSAGE_RESPONSE_SCHEMA


class TgClient:
    """
    Класс для общения с Телеграм API
    """
    def __init__(self, token: Optional[str]) -> None:
        self.token = token

    def get_url(self, method: str) -> str:
        """
        Получаем адрес API Телеграм
        """
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        """
        Проверяем, есть ли для нас сообщение в Телеграм API
        """
        url = self.get_url("getUpdates")
        response = requests.get(url, params={"offset": offset, "timeout": timeout})
        return GET_UPDATES_SCHEMA().load(response.json())

    def send_message_to_url(self, chat_id: int, text: str) -> SendMessageResponse:
        """
        Отправляем сообщение в Телеграм API
        """
        url = self.get_url("sendMessage")
        response = requests.get(url, params={"chat_id": chat_id, "text": text})
        return SEND_MESSAGE_RESPONSE_SCHEMA().load(response.json())



