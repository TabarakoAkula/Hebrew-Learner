from apps.users.models import User
from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(User)
class UsersAdmin(ModelAdmin):
    list_display = (
        "telegram_id",
        "telegram_username",
        "moderator",
        "created_at",
        "updated_at",
    )
    search_fields = ("telegram_id", "telegram_username")
    list_filter = ("moderator", "created_at", "updated_at")
