from django.db import models


class SyncRun(models.Model):
    class Provider(models.TextChoices):
        OMNICOMM = "omnicomm", "Omnicomm"
        RETAILIQA = "retailiqa", "Retailiqa"

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        RUNNING = "running", "Выполняется"
        SUCCESS = "success", "Успешно"
        FAILED = "failed", "Ошибка"

    provider = models.CharField("Провайдер", max_length=20, choices=Provider.choices)
    sync_type = models.CharField("Тип синхронизации", max_length=100)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.PENDING)
    started_at = models.DateTimeField("Начато", null=True, blank=True)
    finished_at = models.DateTimeField("Завершено", null=True, blank=True)
    records_received = models.PositiveIntegerField("Получено записей", default=0)
    records_created = models.PositiveIntegerField("Создано записей", default=0)
    records_updated = models.PositiveIntegerField("Обновлено записей", default=0)
    error_message = models.TextField("Описание ошибки", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Запуск синхронизации"
        verbose_name_plural = "Запуски синхронизации"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.get_provider_display()} — {self.sync_type}"
