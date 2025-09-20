from apps.users.models import User
from django.db import models


class Collection(models.Model):
    name = models.CharField(max_length=120, verbose_name="название")
    is_close = models.BooleanField(default=False, verbose_name="закрытая")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="обновлена")

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="collections",
        verbose_name="владелец",
    )
    data = models.JSONField(default=dict, verbose_name="данные")
    users = models.ManyToManyField(
        User,
        related_name="saved_collections",
        blank=True,
        verbose_name="пользователи",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "коллекцию"
        verbose_name_plural = "коллекции"
