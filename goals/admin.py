from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")


class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "due_date", "user", "created", "updated", "category")
    search_fields = ("title", "user", "description")


class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ("text", "goal", "user", "created", "updated")
    search_fields = ("text", "user")


class BoardAdmin(admin.ModelAdmin):
    list_display = ("title", "is_deleted", "created", "updated")
    search_fields = ("title", )


class BoardParticipantAdmin(admin.ModelAdmin):
    list_display = ("board", "user", "role", "created", "updated")
    search_fields = ("title", )


admin.site.register(GoalCategory, GoalCategoryAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(GoalComment, GoalCommentAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(BoardParticipant, BoardParticipantAdmin)
