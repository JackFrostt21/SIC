from django.db import models


""" Инструкции """


class Instruction(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название инструкции")
    file = models.FileField(
        upload_to="instruction_files/", blank=True, null=True, verbose_name="Файл"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Инструкция"
        verbose_name_plural = "Инструкции"
        ordering = ["name"]


""" Логи активности пользователей бота """


class BotEventLog(models.Model):
    EVENT_MESSAGE = "message"
    EVENT_CALLBACK = "callback"
    EVENT_COMMAND = "command"
    EVENT_ERROR = "error"
    EVENT_SYSTEM = "system"

    EVENT_TYPES = (
        (EVENT_MESSAGE, "Сообщение"),
        (EVENT_CALLBACK, "Кнопка (callback)"),
        (EVENT_COMMAND, "Команда"),
        (EVENT_ERROR, "Ошибка"),
        (EVENT_SYSTEM, "Система"),
    )

    # Ссылка на нашего пользователя (может отсутствовать до регистрации)
    user = models.ForeignKey(
        "bot.TelegramUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
        related_name="event_logs",
    )
    telegram_id = models.BigIntegerField(verbose_name="Telegram ID", db_index=True)
    username = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Username"
    )
    chat_id = models.BigIntegerField(null=True, blank=True, verbose_name="Chat ID")
    update_id = models.BigIntegerField(null=True, blank=True, verbose_name="Update ID")

    event_type = models.CharField(
        max_length=20, choices=EVENT_TYPES, verbose_name="Тип события", db_index=True
    )
    action_key = models.CharField(max_length=64, verbose_name="Действие", db_index=True)
    content_text = models.TextField(null=True, blank=True, verbose_name="Текст/контент")
    data = models.JSONField(null=True, blank=True, verbose_name="Детали")
    handler = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Хендлер"
    )
    state = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="FSM стейт"
    )
    is_private = models.BooleanField(default=True, verbose_name="Личный чат")

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Создано", db_index=True
    )

    class Meta:
        verbose_name = "Событие бота"
        verbose_name_plural = "События бота"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["telegram_id", "created_at"]),
            models.Index(fields=["event_type", "action_key"]),
        ]

    def __str__(self):
        who = (
            self.username
            or (self.user.full_name if self.user else None)
            or f"ID:{self.telegram_id}"
        )
        return f"{self.created_at:%d.%m.%Y %H:%M:%S} • {who} • {self.event_type}:{self.action_key}"
