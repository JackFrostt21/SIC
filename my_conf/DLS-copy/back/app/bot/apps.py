from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.bot"
    verbose_name = "Телеграм бот"

    def ready(self):
        # Импорт сигналов приложения
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Избегаем ошибок импорта при миграциях
            pass
