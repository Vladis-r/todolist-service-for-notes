from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")


class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "due_date", "user", "created", "updated", "category")
    search_fields = ("title", "user", "description")


class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ("text", "goal", "user", "created", "updated")
    search_fields = ("text", "user")


admin.site.register(GoalCategory, GoalCategoryAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(GoalComment, GoalCommentAdmin)
