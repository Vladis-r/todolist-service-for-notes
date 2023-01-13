import typing

from django.http import HttpRequest, HttpResponse
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from bot.management.commands.runbot import Command
from bot.models import TgUser
from bot.serializers import VerifyTgBotSerializer


class VerifyTgBotView(UpdateAPIView):
    """
    Верифицируем токен, выданный в телеграме, на сайте
    """
    model = TgUser
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VerifyTgBotSerializer

    def __init__(self) -> None:
        self.tg_client = Command.tg_client
        super().__init__()

    def patch(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponse:
        data = self.serializer_class(request.data).data
        tg_user = TgUser.objects.filter(verification_code=data["verification_code"]).first()
        if not tg_user:
            return Response(ValidationError)
        tg_user.user = request.user
        tg_user.save()
        self.tg_client.send_message_to_url(chat_id=tg_user.tg_chat_id, text="Верификация прошла успешно")
        return Response(data=data, status=status.HTTP_200_OK)
