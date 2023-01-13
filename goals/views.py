import typing

from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Board
from goals.permissions import BoardPermissions, CategoryPermissions, GoalPermissions, CommentPermissions
from goals.serializers import GoalCreateSerializer, GoalCategorySerializer, GoalCategoryCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, BoardSerializer, \
    BoardListSerializer


class GoalListView(ListAPIView):
    """
    Список целей
    """
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = GoalDateFilter
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title", "description"]

    def get_queryset(self) -> typing.Union[QuerySet, typing.List[Goal]]:
        """
        Фильтруем цели, если они не удалены и мы в них участники
        """
        return Goal.objects.filter(category__board__participants__user=self.request.user).\
            exclude(status=Goal.Status.archived)


class GoalCategoryCreateView(CreateAPIView):
    """
    Создание категории
    """
    model = GoalCategory
    serializer_class = GoalCategoryCreateSerializer
    permission_classes = [permissions.IsAuthenticated, CategoryPermissions]


class GoalCategoryListView(ListAPIView):
    """
    Список категорий
    """
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["title", "created", "board"]
    ordering = ["title"]
    search_fields = ["title", "board"]

    def get_queryset(self) -> typing.Union[QuerySet, typing.List[GoalCategory]]:
        """
        Фильтруем категории, если они не удалены и мы в них участники
        """
        return GoalCategory.objects.filter(board__participants__user=self.request.user, is_deleted=False)


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """
    Просмотр, удаление и обновление категории
    """
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, CategoryPermissions]

    def get_queryset(self) -> typing.Union[QuerySet, typing.List[GoalCategory]]:
        """
        Фильтруем категории, если они не удалены и мы в них участники
        """
        return GoalCategory.objects.filter(board__participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: GoalCategory) -> GoalCategory:
        """
        При удалении категории меняем флаг is_deleted и сохраняем в бд
        """
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.goals.update(status=Goal.Status.archived)
        return instance


class GoalCreateView(CreateAPIView):
    """
    Создание цели
    """
    models = Goal
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]
    serializer_class = GoalCreateSerializer


class GoalView(RetrieveUpdateDestroyAPIView):
    """
    Просмотр, удаление, обновление цели
    """
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]

    def get_queryset(self) -> typing.Union[QuerySet, typing.List[Goal]]:
        """
        Фильтруем цели, если они не удалены и мы в них участники
        """
        return Goal.objects.filter(category__board__participants__user=self.request.user)

    def perform_destroy(self, instance: Goal) -> Goal:
        """
        При удалении цели, меняем её статус на archived и сохраняем в бд
        """
        instance.status = Goal.Status.archived
        instance.save()
        return instance


class GoalCommentCreateView(CreateAPIView):
    """
    Создание комментария
    """
    models = GoalComment
    permission_classes = [permissions.IsAuthenticated, CommentPermissions]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
    """
    Просмотр списка комментариев
    """
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["goal"]
    ordering = ["-created"]

    def get_queryset(self) -> typing.Union[QuerySet, typing.List[GoalComment]]:
        """
        Фильтруем комментарии, в которых мы являемся участниками
        """
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """
    Просмотр, удаление, обновление комментария
    """
    model = GoalComment
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated, CommentPermissions]

    def get_queryset(self) -> typing.Union[QuerySet, typing.List[GoalComment]]:
        """
        Фильтруем комментарии, в которых мы являемся участниками
        """
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class BoardCreateView(CreateAPIView):
    """
    Создание доски
    """
    model = Board
    serializer_class = BoardCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class BoardView(RetrieveUpdateDestroyAPIView):
    """
    Просмотр, удаление, обновление доски
    """
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self) -> typing.Union[QuerySet, typing.List[Board]]:
        """
        Фильтруем доски, если они не удалены и мы в них участники
        """
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: Board) -> Board:
        """
        При удалении доски ставим флаг is_deleted, категориям так же ставится флаг is_deleted,
        а целям статус archived. После чего сохраняем их в бд.

        """
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
        return instance


class BoardListView(ListAPIView):
    """
    Просмотр доски
    """
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardListSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ["title"]

    def get_queryset(self) -> typing.Union[QuerySet, typing.List[Board]]:
        """
        Фильтруем доски, если они не удалены и мы в них участники
        """
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)
