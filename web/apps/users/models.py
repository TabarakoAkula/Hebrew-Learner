from django.db import models


class User(models.Model):
    telegram_id = models.CharField(
        max_length=120,
        verbose_name="telegram id",
        unique=True,
    )
    telegram_username = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name="имя пользователя",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="обновлен")
    moderator = models.BooleanField(default=False, verbose_name="модератор")

    def __str__(self):
        if self.telegram_username:
            return self.telegram_username
        return "unknown"

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
