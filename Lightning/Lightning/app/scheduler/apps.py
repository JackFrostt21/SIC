from django.apps import AppConfig
import os
import sys


class SchedulerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.scheduler"
    verbose_name = "Планировщик"

    def ready(self):
        """Стартуем планировщик один раз при запуске приложения.

        Защиты от двойного старта:
        - Не запускаем во время миграций/collectstatic.
        - Не запускаем в процессе телеграм-бота (команда 'bot').
        - Для dev runserver учитываем переменную RUN_MAIN.
        """
        try:
            # 1) Команды, в которых запускать не нужно
            argv = sys.argv
            management_cmd = argv[1] if len(argv) > 1 else ""
            skip_commands = {
                "migrate",
                "makemigrations",
                "collectstatic",
                "shell",
                "dbshell",
                "loaddata",
                "dumpdata",
                "test",
            }
            if management_cmd in skip_commands:
                return

            # 2) Процесс бота — не стартуем планировщик
            if management_cmd == "bot":
                return

            # 3) Dev runserver двойной старт — запускаем только в дочернем процессе
            if management_cmd == "runserver" and os.environ.get("RUN_MAIN") != "true":
                return

            # 4) Стартуем наш планировщик
            from app.scheduler.scheduling import start_scheduler

            start_scheduler()
        except Exception:
            # Логируем, но не падаем, чтобы не мешать запуску Django
            import logging

            logging.getLogger(__name__).exception(
                "Ошибка запуска планировщика в AppConfig.ready"
            )
