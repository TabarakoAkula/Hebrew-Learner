from apps.words.models import Word
from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(Word)
class WordsAdmin(ModelAdmin):
    list_display = (
        "hebrew_word",
        "pealim_link",
        "analyzed",
        "multiply",
        "created_at",
        "updated_at",
    )
    search_fields = ("hebrew_word",)
    list_filter = ("hebrew_word", "created_at", "updated_at")
