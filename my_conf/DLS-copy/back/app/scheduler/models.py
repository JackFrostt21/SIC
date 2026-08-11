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


class ReminderSetting(models.Model):
    """
    Настройки рассылки напоминаний о непройденных курсах.
    """

    name = models.CharField(
        max_length=200,
        default="Настройка напоминаний",
        verbose_name="Наименование настройки",
    )
    enable_gif = models.BooleanField(
        default=False,
        verbose_name="Отправлять GIF перед сообщением",
        help_text="Если включено и загружен GIF, отправлять анимацию перед текстом",
    )
    gif = models.FileField(
        upload_to="gif_reminder/",
        blank=True,
        null=True,
        verbose_name="Общий GIF для напоминаний",
    )

    # Планирование
    enable_scheduler = models.BooleanField(
        default=True,
        verbose_name="Включить планировщик напоминаний",
    )
    schedule_start_hour = models.PositiveSmallIntegerField(
        default=10,
        verbose_name="Час запуска",
        help_text="Час в 24-часовом формате (0-23), от которого строятся слоты",
    )
    schedule_interval_hours = models.FloatField(
        default=24.0,
        verbose_name="Интервал повтора (часы)",
        help_text="Шаг между слотами в часах; ≤0 трактуется как 24",
    )
    poll_interval_minutes = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Период опроса (мин)",
        help_text="Как часто поллер проверяет, пора ли запускать рассылку",
    )

    # Дни недели
    monday = models.BooleanField(default=True, verbose_name="Понедельник")
    tuesday = models.BooleanField(default=True, verbose_name="Вторник")
    wednesday = models.BooleanField(default=True, verbose_name="Среда")
    thursday = models.BooleanField(default=True, verbose_name="Четверг")
    friday = models.BooleanField(default=True, verbose_name="Пятница")
    saturday = models.BooleanField(default=True, verbose_name="Суббота")
    sunday = models.BooleanField(default=True, verbose_name="Воскресенье")

    # Отправка
    batch_size = models.PositiveSmallIntegerField(
        default=25,
        verbose_name="Размер пакета",
        help_text="Количество пользователей в одном пакете",
    )
    delay_between_users = models.FloatField(
        default=0.15,
        verbose_name="Задержка между пользователями (сек)",
        help_text="Пауза между отправками в рамках пакета",
    )
    delay_between_batches = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="Задержка между пакетами (сек)",
        help_text="Пауза между обработкой батчей",
    )
    max_retry_attempts = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Макс. число попыток",
        help_text="Сколько раз повторять отправку после ошибок",
    )
    cleanup_age_days = models.PositiveSmallIntegerField(
        default=30,
        verbose_name="Дни до очистки логов",
        help_text="Старше скольких дней удалять записи SchedulerLog",
    )

    class Meta:
        verbose_name = "Настройки напоминаний"
        verbose_name_plural = "Настройки напоминаний"

    def __str__(self):
        return self.name

    @property
    def active_days(self):
        days = []
        if self.monday:
            days.append(0)
        if self.tuesday:
            days.append(1)
        if self.wednesday:
            days.append(2)
        if self.thursday:
            days.append(3)
        if self.friday:
            days.append(4)
        if self.saturday:
            days.append(5)
        if self.sunday:
            days.append(6)
        return days
