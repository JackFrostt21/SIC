from django.contrib import admin

from app.scheduler.models import SchedulerLog, ReminderSetting


@admin.register(SchedulerLog)
class SchedulerLogAdmin(admin.ModelAdmin):
    list_display = (
        "task_name",
        "status",
        "start_time",
        "end_time",
        "execution_time",
        "total_messages_sent",
        "total_errors",
    )
    list_filter = ("status", "task_name", "start_time")
    search_fields = ("task_name", "error_message")
    ordering = ("-start_time",)


@admin.register(ReminderSetting)
class ReminderSettingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "enable_scheduler",
        "schedule_start_hour",
        "schedule_interval_hours",
        "poll_interval_minutes",
        "batch_size",
    )
    list_filter = (
        "enable_scheduler",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    search_fields = ("name",)
    ordering = ("name",)

    fieldsets = (
        ("Общее", {"fields": ("name", "gif", "enable_gif")}),
        (
            "Планировщик",
            {
                "fields": (
                    "enable_scheduler",
                    "schedule_start_hour",
                    "schedule_interval_hours",
                    "poll_interval_minutes",
                )
            },
        ),
        (
            "Дни недели",
            {
                "fields": (
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                )
            },
        ),
        (
            "Отправка",
            {
                "fields": (
                    "batch_size",
                    "delay_between_users",
                    "delay_between_batches",
                    "max_retry_attempts",
                )
            },
        ),
        ("Очистка", {"fields": ("cleanup_age_days",)}),
    )
