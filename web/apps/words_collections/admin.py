from apps.words_collections.models import Collection
from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(Collection)
class CollectionsAdmin(ModelAdmin):
    list_display = (
        "name",
        "is_close",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    list_filter = ("is_close", "created_at", "updated_at")
