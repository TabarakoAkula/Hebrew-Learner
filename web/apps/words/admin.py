from apps.words.models import Word, Category
from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(Word)
class WordsAdmin(ModelAdmin):
    list_display = (
        "hebrew_word",
        "category",
        "pealim_link",
        "data",
        "created_at",
        "updated_at",
    )
    search_fields = ("hebrew_word", "category")
    list_filter = ("hebrew_word", "category", "created_at", "updated_at")


@admin.register(Category)
class CategoriesAdmin(ModelAdmin):
    list_display = (
        "hebrew_name",
        "russian_name",
    )
    search_fields = ("hebrew_name", "russian_name")
    list_filter = ("hebrew_name", "russian_name")
