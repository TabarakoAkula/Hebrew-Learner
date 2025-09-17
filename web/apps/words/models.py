from django.db import models


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
    analyzed = models.BooleanField(default=False, verbose_name="анализирован")
    multiply = models.BooleanField(default=False, verbose_name="множественное")

    def __str__(self):
        return self.hebrew_word

    class Meta:
        verbose_name = "слово"
        verbose_name_plural = "слова"
