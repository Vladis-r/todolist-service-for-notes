import typing
from typing import Union

from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.generics import GenericAPIView

from goals.models import BoardParticipant


class BoardPermissions(permissions.BasePermission):
    """
    Если пользователь не аутентифицирован, то возвращает False.
    При SAFE методах возвращает True.
    Остальные методы доступны только пользователю с ролью "владелец" (owner)
    """
    def has_object_permission(self, request: HttpRequest, view: GenericAPIView, obj: typing.Any) -> bool:
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj
            ).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner
        ).exists()


class CategoryPermissions(permissions.BasePermission):
    """
    При SAFE методах возвращает True.
    Остальные методы доступны только пользователю с ролью "владелец" (owner) или "редактор" (writer)
    """
    def has_object_permission(self, request: HttpRequest, view: GenericAPIView, obj: typing.Any) -> bool:
        if request.method not in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj.board,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
            ).exists()
        return True


class GoalPermissions(permissions.BasePermission):
    """
    При SAFE методах возвращает True.
    Остальные методы доступны только пользователю с ролью "владелец" (owner) или "редактор" (writer)
    """
    def has_object_permission(self, request: HttpRequest, view: GenericAPIView, obj: typing.Any) -> bool:
        if request.method not in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj.category.board,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
            ).exists()
        return True


class CommentPermissions(permissions.BasePermission):
    """
    При SAFE методах возвращает True.
    Остальные методы доступны только пользователю с ролью "владелец" (owner) или "редактор" (writer)
    """
    def has_object_permission(self, request: HttpRequest, view: GenericAPIView, obj: typing.Any) -> bool:
        if request.method not in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj.goal.category.board,
            ).exists()
        if obj.user != request.user:
            return False
        return True
