from django.db import models
from django.conf import settings

# Константы на уровне модуля (в верхнем регистре)
PROJECT_STATUS_OPEN = "open"
PROJECT_STATUS_CLOSED = "closed"
PROJECT_STATUS_CHOICES = [
    (PROJECT_STATUS_OPEN, "Открыт"),
    (PROJECT_STATUS_CLOSED, "Закрыт"),
]


# Максимальная длина полей
MAX_NAME_LENGTH = 200
MAX_STATUS_LENGTH = 6


class Project(models.Model):
    STATUS_CHOICES = PROJECT_STATUS_CHOICES
    name = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    github_url = models.URLField(blank=True, verbose_name="Ссылка на GitHub")
    status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
        verbose_name="Статус",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
