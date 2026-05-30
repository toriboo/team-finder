# projects/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Project, PROJECT_STATUS_OPEN, PROJECT_STATUS_CLOSED


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "status", "created_at", "participants_count")
    list_filter = ("status", "created_at", "owner")
    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__name",
        "owner__surname",
    )
    readonly_fields = ("created_at",)
    filter_horizontal = ("participants",)
    fieldsets = (
        (None, {"fields": ("name", "description", "github_url")}),
        (_("Author & Status"), {"fields": ("owner", "status")}),
        (_("Participants"), {"fields": ("participants",)}),
        (_("Dates"), {"fields": ("created_at",), "classes": ("collapse",)}),
    )
    actions = ["make_open", "make_closed"]

    def participants_count(self, obj):
        return obj.participants.count()

    participants_count.short_description = _("Кол-во участников")

    def make_open(self, request, queryset):
        queryset.update(status=PROJECT_STATUS_OPEN)

    make_open.short_description = _("Открыть выбранные проекты")

    def make_closed(self, request, queryset):
        queryset.update(status=PROJECT_STATUS_CLOSED)

    make_closed.short_description = _("Закрыть выбранные проекты")
