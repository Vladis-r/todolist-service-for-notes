import typing

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from core.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    def validate(self, attrs: typing.Any) -> typing.Any:
        """
        Забираем данные пароля и повтор_пароля, проходим проверки и возвращаем
        """
        password = attrs.get("password")
        password_repeat = attrs.pop("password_repeat")

        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError({"password": e})

        if password != password_repeat:
            raise serializers.ValidationError("Passwords do not match")

        return attrs

    def create(self, validated_data: typing.Any) -> typing.Any:
        """
        Валидируем и хешируем пароль, создаём пользователя в бд
        """
        password = validated_data.get("password")
        validated_data["password"] = make_password(password)
        return super().create(validated_data)

    class Meta:
        model = User
        fields = "__all__"


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def create(self, validated_data: dict) -> User:
        """
        Аутентифицируем пользователя
        """
        if not (user := authenticate(
            username=validated_data['username'],
            password=validated_data['password'],
        )):
            raise AuthenticationFailed
        return user

    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")


class UpdatePasswordSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    old_password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs: typing.Any) -> typing.Any:
        """
        Обновление пароля пользователя.
        Проверяем старый пароль, валидируем новый и возвращаем
        """
        user = attrs["user"]
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "incorrect password"})

        try:
            validate_password(attrs["new_password"])
        except Exception as e:
            raise serializers.ValidationError({"new_password": e})

        return attrs

    def update(self, instance: User, validated_data: typing.Any) -> User:
        """
        Хешируем и сохраняем пароль
        """
        instance.password = make_password(validated_data["new_password"])
        instance.save()
        return instance

