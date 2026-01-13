from django.db import models


class SchedulerLog(models.Model):
    TASK_STATUS_CHOICES = (
        ("pending", "В ожидании"),
        ("running", "Выполняется"),
        ("completed", "Завершено успешно"),
        ("failed", "Ошибка выполнения"),
    )

    task_name = models.CharField(max_length=100, verbose_name="Название задачи")
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default="pending",
        verbose_name="Статус",
    )
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Время начала")
    end_time = models.DateTimeField(
        null=True, blank=True, verbose_name="Время завершения"
    )
    execution_time = models.FloatField(
        null=True, blank=True, verbose_name="Время выполнения (сек)"
    )
    error_message = models.TextField(
        null=True, blank=True, verbose_name="Сообщение об ошибке"
    )
    total_messages_sent = models.PositiveIntegerField(
        default=0, verbose_name="Всего отправлено сообщений"
    )
    total_errors = models.PositiveIntegerField(
        default=0, verbose_name="Количество ошибок"
    )
    additional_info = models.JSONField(
        null=True, blank=True, verbose_name="Дополнительная информация"
    )

    class Meta:
        verbose_name = "Лог планировщика"
        verbose_name_plural = "Логи планировщика"
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.task_name} ({self.start_time.strftime('%d.%m.%Y %H:%M:%S')}) - {self.get_status_display()}"