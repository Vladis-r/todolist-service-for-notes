import requests

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse, GET_UPDATES_SCHEMA, SEND_MESSAGE_RESPONSE_SCHEMA
from todolist.settings import TG_TOKEN


class TgClient:
    def __init__(self, token):
        self.token = token

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url("getUpdates")
        response = requests.get(url, params={"offset": offset, "timeout": timeout})
        return GET_UPDATES_SCHEMA().load(response.json())

    def send_message_to_url(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url("sendMessage")
        response = requests.get(url, params={"chat_id": chat_id, "text": text})
        return SEND_MESSAGE_RESPONSE_SCHEMA().load(response.json())


tg_client = TgClient(TG_TOKEN)
