# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "name", "surname", "phone", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "skills")
    search_fields = ("email", "name", "surname", "phone")
    filter_horizontal = ("skills",)
    readonly_fields = ("last_login",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")},
        ),
        (_("Skills"), {"fields": ("skills",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    ordering = ("email",)
