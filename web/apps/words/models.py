from django.db import models


class Category(models.Model):
    hebrew_name = models.CharField(null=False, blank=False, max_length=120, verbose_name="название на иврите")
    russian_name = models.CharField(null=False, blank=False, max_length=120, verbose_name="название на русском")

    def __str__(self):
        return f"{self.hebrew_name} | {self.russian_name}"

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"


class Word(models.Model):
    hebrew_word = models.CharField(null=False, blank=False, max_length=120, verbose_name="слово на иврите")
    data = models.JSONField(default=dict, null=True, blank=True, verbose_name="информация")
    pealim_link = models.URLField(null=True, blank=True, verbose_name="ссылка на Pealim")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="обновлен")
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        related_name="words",
        on_delete=models.CASCADE,
        verbose_name="категория",
    )

    def __str__(self):
        return self.hebrew_word

    class Meta:
        verbose_name = "слово"
        verbose_name_plural = "слова"
