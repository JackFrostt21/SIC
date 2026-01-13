from django.contrib import admin
from django.db.models import Q
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX, XLS, CSV
from asgiref.sync import async_to_sync
from datetime import datetime

from .models import TelegramUser, TelegramGroup
from .resources import TelegramUserResource, TelegramGroupResource
from app.integration.models import APISettings
from app.integration.services.onec_client import build_onec_payload, post_onec
from app.integration.services.onec_mapping import apply_employee_from_onec


class GuidAcceptFilter(admin.SimpleListFilter):
    title = "1С проверка"
    parameter_name = "guid_accept"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Подтвержден"),
            ("no", "Не подтвержден"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "yes":
            return queryset.exclude(Q(guid_1c__isnull=True) | Q(guid_1c__exact=""))
        if value == "no":
            return queryset.filter(Q(guid_1c__isnull=True) | Q(guid_1c__exact=""))
        return queryset


@admin.register(TelegramUser)
class TelegramUserAdmin(ImportExportModelAdmin):
    resource_class = TelegramUserResource
    actions = ("sync_with_onec",)
    list_display = (
        "username",
        "full_name",
        "phone",
        "department",
        "job_title",
        "guid_accept",
        "state",
        "last_activity",
        "created_at",
    )
    list_filter = ("company", "department", "job_title", "state", GuidAcceptFilter, "created_at")
    search_fields = ("telegram_id", "username", "full_name", "phone")
    ordering = ("full_name",)
    list_display_links = ("username",)
    readonly_fields = (
        "telegram_id",
        "username",
        "last_activity",
        "guid_1c",
        "guid_accept",
        "created_at",
        "updated_at",
    )

    formats = (XLSX, XLS, CSV)

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "guid_1c",
                    "guid_accept",
                    "telegram_id",
                    "username",
                    "full_name",
                    "image",
                )
            },
        ),
        (
            "Личные данные",
            {
                "fields": (
                    "last_name",
                    "first_name",
                    "middle_name",
                    "date_of_birth",
                    "phone",
                    "email",
                )
            },
        ),
        (
            "Организация",
            {
                "fields": (
                    "company",
                    "department",
                    "job_title",
                )
            },
        ),
        ("Статус", {"fields": ("state", "language", "last_activity")}),
        ("Дата создания", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="1С проверка", boolean=True)
    def guid_accept(self, obj):
        return bool(obj.guid_1c)

    def _to_iso_date(self, value: str):
        if not value:
            return None
        s = str(value).strip()
        # Поддержим оба формата: DD.MM.YYYY и YYYY-MM-DD
        for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
            except Exception:
                continue
        return None

    def sync_with_onec(self, request, queryset):
        settings = APISettings.objects.select_related("company").first()
        if (
            not settings
            or not settings.api_url
            or not settings.api_username
            or not settings.api_password
        ):
            self.message_user(
                request,
                "Не настроены параметры API 1С (app.integration.models.APISettings).",
                level=20,
            )
            return

        success, skipped, errors = 0, 0, 0

        for user in queryset:
            last_name = (user.last_name or "").strip()
            first_name = (user.first_name or "").strip()
            middle_name = (user.middle_name or "").strip() or None
            birthday_iso = self._to_iso_date(user.date_of_birth or "")

            if not last_name or not first_name or not birthday_iso:
                skipped += 1
                continue

            payload = build_onec_payload(
                last_name=last_name, name=first_name, birthday_iso=birthday_iso
            )

            try:
                response = async_to_sync(post_onec)(
                    url=settings.api_url,
                    username=settings.api_username,
                    password=settings.api_password,
                    payload=payload,
                    timeout_seconds=10.0,
                )
            except Exception:
                errors += 1
                continue

            try:
                records = (
                    (response or {}).get("data") if isinstance(response, dict) else None
                )
                if records and isinstance(records, list) and records:
                    employee = records[0]
                    # Применяем данные к пользователю
                    apply_employee_from_onec(
                        employee=employee,
                        company=settings.company,
                        telegram_id=user.telegram_id,
                        username=user.username,
                        last_name=last_name,
                        first_name=first_name,
                        middle_name=middle_name,
                    )

                    # Обновим статус, если 1С вернула 0
                    status_from_onec = employee.get("status")
                    if status_from_onec == 0 and hasattr(TelegramUser, "STATE_DELETED"):
                        user.state = TelegramUser.STATE_DELETED
                        user.save(update_fields=("state",))
                    elif hasattr(TelegramUser, "STATE_ACTIVE"):
                        user.state = TelegramUser.STATE_ACTIVE
                        user.save(update_fields=("state",))

                    success += 1
                else:
                    errors += 1
            except Exception:
                errors += 1

        self.message_user(
            request,
            f"Синхронизация завершена. Успешно: {success}, пропущено: {skipped}, ошибок: {errors}",
        )

    sync_with_onec.short_description = "Синхронизировать с 1С"


@admin.register(TelegramGroup)
class TelegramGroupAdmin(ImportExportModelAdmin):
    resource_class = TelegramGroupResource
    list_display = ("name", "user_count")
    search_fields = ("name",)
    filter_horizontal = ("users",)

    formats = (XLSX, XLS, CSV)

    def user_count(self, obj):
        return obj.users.count()

    user_count.short_description = "Количество пользователей"
