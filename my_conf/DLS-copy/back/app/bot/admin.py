from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX, XLS, CSV
from .models import (
    TelegramUser,
    TelegramGroup,
    UserRead,
    UserTest,
    CustomUser,
    PasswordResetToken,
    UserRating,
    SubscriptionUser,
)
from .resources import TelegramUserResource, TelegramGroupResource


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "is_superuser")


@admin.register(TelegramUser)
class TelegramUserAdmin(ImportExportModelAdmin):
    resource_class = TelegramUserResource
    list_display = (
        "telegram_id",
        "full_name",
        "user_name",
        "phone",
        "email",
        "company",
        "department",
        "job_title",
        "state",
        "is_actual",
    )
    list_filter = (
        "is_actual",
        "state",
        "company",
        "department",
        "job_title",
        "language",
    )
    search_fields = (
        "telegram_id",
        "full_name",
        "user_name",
        "phone",
        "email",
        "first_name",
        "last_name",
    )
    readonly_fields = ("created_at", "updated_at")

    # Форматы для импорта/экспорта
    formats = [XLSX, XLS, CSV]

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "telegram_id",
                    "guid_1c",
                    "user_name",
                    "full_name",
                    "image",
                    "created_at",
                    "updated_at",
                    "personal_data_consent",
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
        ("Организация", {"fields": ("company", "department", "job_title")}),
        ("Настройки и состояние", {"fields": ("language", "is_actual", "state")}),
    )


@admin.register(TelegramGroup)
class TelegramGroupAdmin(ImportExportModelAdmin):
    resource_class = TelegramGroupResource
    list_display = ("name", "description_short", "user_count", "is_actual")
    list_filter = ("is_actual", "created_at")
    search_fields = ("name", "description")
    filter_horizontal = ("users",)
    readonly_fields = ("created_at", "updated_at")

    # Форматы для импорта/экспорта
    formats = [XLSX, XLS, CSV]

    def description_short(self, obj):
        if obj.description and len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description or "-"

    description_short.short_description = "Описание"

    def user_count(self, obj):
        return obj.users.count()

    user_count.short_description = "Кол-во пользователей"


@admin.register(UserRead)
class UserReadAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "topic", "is_read", "read_at")
    list_filter = ("is_read", "read_at", "course", "topic")
    search_fields = (
        "user__full_name",
        "user__user_name",
        "course__title",
        "topic__title",
    )
    date_hierarchy = "read_at"
    readonly_fields = ("created_at", "updated_at")


@admin.register(UserTest)
class UserTestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "training",
        "course_topic",
        "complete",
        "results_display",
        "created_at",
    )
    list_filter = ("complete", "training", "course_topic")
    search_fields = (
        "user__full_name",
        "user__user_name",
        "training__title",
        "course_topic__title",
    )
    readonly_fields = ("user_answer", "created_at", "updated_at")
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "user",
                    "training",
                    "course_topic",
                    "is_actual",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Результаты",
            {"fields": ("complete", "quantity_correct", "quantity_not_correct")},
        ),
        # Поле с ответами пока скрыл, словарь с результатами был пустой, сейчас от фронта также получаю без детализации, оставлю на потом
        # (
        #     "Ответы пользователя",
        #     {
        #         "classes": ("collapse",),  # скрывает поле ответы пользователя
        #         "fields": ("user_answer",),  # показывает поле ответы пользователя
        #     },
        # ),
    )

    def results_display(self, obj):
        if obj.quantity_correct is not None:
            return format_html(
                '<span style="color: {};">{} / {}</span>',
                "green" if obj.complete else "red",
                obj.quantity_correct or 0,
                100,
            )
        return "-"

    results_display.short_description = "Результаты"


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "expires_at", "is_used", "ip_address")
    list_filter = ("is_used", "created_at", "expires_at")
    search_fields = ("user__username", "user__email", "token")
    readonly_fields = ("token", "created_at", "expires_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        # Запрещаем создание токенов через админку
        return False

    def has_change_permission(self, request, obj=None):
        # Разрешаем только просмотр
        return False


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "points", "updated_at")
    search_fields = ("user__full_name", "user__user_name")
    ordering = ("-points", "user__id")
    readonly_fields = ("created_at", "updated_at")

@admin.register(SubscriptionUser)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__full_name", "user__user_name")
    ordering = ("-created_at", "user__id")
    readonly_fields = ("created_at", "updated_at")
