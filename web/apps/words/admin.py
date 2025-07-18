from apps.words.models import Category, Word
from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(Word)
class WordsAdmin(ModelAdmin):
    list_display = (
        "hebrew_word",
        "pealim_link",
        "get_categories",
        "analyzed",
        "multiply",
        "created_at",
        "updated_at",
    )
    search_fields = ("hebrew_word", "category")
    list_filter = ("hebrew_word", "created_at", "updated_at")

    def get_categories(self, obj):
        return " | ".join([category.russian_name for category in obj.categories.all()])

    get_categories.short_description = "категории"


@admin.register(Category)
class CategoriesAdmin(ModelAdmin):
    list_display = (
        "hebrew_name",
        "russian_name",
    )
    search_fields = ("hebrew_name", "russian_name")
    list_filter = ("hebrew_name", "russian_name")
