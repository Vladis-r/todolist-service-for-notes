from django.contrib import admin

from core.models import User


# admin.site.register(User)


@admin.register(User)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("email", "first_name", "last_name", "username")
    fields = ("username", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined", "last_login")
    readonly_fields = ("date_joined", "last_login")
