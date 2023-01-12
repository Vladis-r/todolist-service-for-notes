from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import VerifyTgBotSerializer
from bot.tg.client import tg_client


class VerifyTgBotView(UpdateAPIView):
    model = TgUser
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VerifyTgBotSerializer

    def __init__(self):
        self.tg_client = tg_client
        super().__init__()

    def patch(self, request, *args, **kwargs):
        data = self.serializer_class(request.data).data
        tg_user = TgUser.objects.filter(verification_code=data["verification_code"]).first()
        if not tg_user:
            return Response(ValidationError)
        tg_user.user = request.user
        tg_user.save()
        tg_client.send_message_to_url(chat_id=tg_user.tg_chat_id, text="Верификация прошла успешно")
        return Response(data=data, status=status.HTTP_200_OK)
