from django.contrib import admin

from unfold.admin import ModelAdmin

from apps.integrations.models import SyncRun


@admin.register(SyncRun)
class SyncRunAdmin(ModelAdmin):
    list_display = (
        "provider",
        "sync_type",
        "status",
        "started_at",
        "finished_at",
        "records_received",
        "records_created",
        "records_updated",
    )
    list_filter = ("provider", "status")
    search_fields = ("sync_type", "error_message")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
