from django.contrib import admin

from .models import Instruction, BotEventLog


@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(BotEventLog)
class BotEventLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user",
        "telegram_id",
        "event_type",
        "action_key",
        "short_text",
        "state",
        "handler",
    )
    list_filter = ("event_type", "action_key", "is_private", "created_at")
    search_fields = ("username", "telegram_id", "content_text")
    raw_id_fields = ("user",)
    readonly_fields = (
        "created_at",
        "user",
        "telegram_id",
        "username",
        "chat_id",
        "update_id",
        "event_type",
        "action_key",
        "content_text",
        "data",
        "handler",
        "state",
    )
    date_hierarchy = "created_at"

    def short_text(self, obj: BotEventLog):
        if not obj.content_text:
            return ""
        s = obj.content_text
        return (s[:80] + "…") if len(s) > 80 else s

    short_text.short_description = "Текст"
