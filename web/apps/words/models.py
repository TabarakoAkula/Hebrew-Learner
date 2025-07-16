from django.db import models


class Category(models.Model):
    hebrew_name = models.CharField(
        null=False,
        blank=False,
        max_length=120,
        verbose_name="название на иврите",
        unique=True,
    )
    russian_name = models.CharField(
        null=False,
        blank=False,
        max_length=120,
        verbose_name="название на русском",
    )

    def __str__(self):
        return f"{self.hebrew_name} | {self.russian_name}"

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"


class Word(models.Model):
    hebrew_word = models.CharField(
        null=False,
        blank=False,
        max_length=120,
        verbose_name="слово на иврите",
        unique=True,
    )
    data = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        verbose_name="информация",
    )
    pealim_link = models.URLField(
        null=True,
        blank=True,
        verbose_name="ссылка на Pealim",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="обновлен")
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="words",
        verbose_name="категория",
    )
    analyzed = models.BooleanField(default=False, verbose_name="анализирован")

    def __str__(self):
        return self.hebrew_word

    class Meta:
        verbose_name = "слово"
        verbose_name_plural = "слова"
