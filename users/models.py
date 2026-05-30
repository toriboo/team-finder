from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from .managers import UserManager
from .utils import generate_avatar

# Константы на уровне модуля
MAX_NAME_LENGTH = 124
MAX_PHONE_LENGTH = 12
MAX_ABOUT_LENGTH = 256
AVATAR_UPLOAD_DIR = "avatars/"
DEFAULT_AVATAR_PATH = "avatars/default.png"


class Skill(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH, unique=True, verbose_name="Название"
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name="Имя")
    surname = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to=AVATAR_UPLOAD_DIR, default=DEFAULT_AVATAR_PATH, verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=MAX_PHONE_LENGTH,
        unique=True,
        validators=[
            RegexValidator(r"^(\+7|8)?\d{10}$", message="Некорректный номер телефона")
        ],
        verbose_name="Телефон",
    )
    github_url = models.URLField(blank=True, verbose_name="GitHub")
    about = models.TextField(
        max_length=MAX_ABOUT_LENGTH, blank=True, verbose_name="О себе"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")

    skills = models.ManyToManyField(
        Skill, related_name="users", blank=True, verbose_name="Навыки"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = generate_avatar(self.name)

        if self.phone and self.phone.startswith("8"):
            self.phone = "+7" + self.phone[1:]

        super().save(*args, **kwargs)
