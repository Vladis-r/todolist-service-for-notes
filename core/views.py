import typing

from django.contrib.auth import login, logout
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from core.models import User
from core.serializers import RegisterSerializer, LoginSerializer, ProfileSerializer, UpdatePasswordSerializer


class RegisterView(CreateAPIView):
    """
    Регистрируем пользователя
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class LoginView(CreateAPIView):
    """
    Аутентифицируем пользователя
    """
    queryset = User.objects.all()
    serializer_class = LoginSerializer

    def create(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> HttpResponse:
        """
        Получаем данные от пользователя и проверяем их
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer: Serializer) -> None:
        """
        Создаём пользователя и аутентифицируем
        """
        user = serializer.save()
        login(request=self.request, user=user)


class ProfileView(RetrieveUpdateDestroyAPIView):
    """
    Страничка пользователя
    """
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]

    def get_object(self) -> User:
        """
        Забираем пользователя из запроса
        """
        return self.request.user

    def delete(self, request: HttpResponse, *args: typing.Any, **kwargs: typing.Any) -> HttpResponse:
        """
        Пользователь заканчивает сессию
        """
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdatePasswordView(UpdateAPIView):
    """
    Обновление пароля пользователя
    """
    serializer_class = UpdatePasswordSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]

    def get_object(self) -> User:
        """
        Забираем пользователя из запроса
        """
        return self.request.user
