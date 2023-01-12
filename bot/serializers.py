from rest_framework import serializers

from bot.models import TgUser


class VerifyTgBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = ("verification_code", )
