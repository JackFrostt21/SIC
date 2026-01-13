from django.db import models
from app.lightning.models.lightning_models import Lightning


class LightningSetting(models.Model):
    name = models.CharField(
        max_length=200,
        default="Настройка оповещений",
        verbose_name="Наименование настройки",
    )
    gif = models.FileField(
        upload_to="gif_lightning/",
        blank=True,
        null=True,
        verbose_name="Общий GIF для молний",
    )
    enable_gif = models.BooleanField(
        default=False,
        verbose_name="Отправлять GIF перед сообщением",
        help_text="Если включено и загружен GIF, отправлять анимацию перед текстом",
    )

    """ Настройки планирования повторных оповещений """
    enable_scheduler = models.BooleanField(
        default=True,
        verbose_name="Включить планировщик повторных оповещений",
    )
    schedule_start_hour = models.PositiveSmallIntegerField(
        default=10,
        verbose_name="Час запуска",
        help_text="Час в 24-часовом формате для запуска задачи отправки (0-23)",
    )
    schedule_interval_hours = models.FloatField(
        default=24.0,
        verbose_name="Интервал повтора (часы)",
        help_text="Как часто запускать задачу отправки (в часах)",
    )
    poll_interval_minutes = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Период опроса планировщика (мин)",
        help_text="Как часто поллер проверяет, пора ли запускать рассылку",
    )
    # Дни недели для планировщика
    monday = models.BooleanField(default=True, verbose_name="Понедельник")
    tuesday = models.BooleanField(default=True, verbose_name="Вторник")
    wednesday = models.BooleanField(default=True, verbose_name="Среда")
    thursday = models.BooleanField(default=True, verbose_name="Четверг")
    friday = models.BooleanField(default=True, verbose_name="Пятница")
    saturday = models.BooleanField(default=True, verbose_name="Суббота")
    sunday = models.BooleanField(default=True, verbose_name="Воскресенье")
    # Настройки отправки
    batch_size = models.PositiveSmallIntegerField(
        default=25,
        verbose_name="Размер пакета",
        help_text="Количество сообщений в одном пакете",
    )
    delay_between_users = models.FloatField(
        default=0.15,
        verbose_name="Задержка между пользователями (сек)",
        help_text="Пауза между отправкой сообщений разным пользователям в одном пакете",
    )
    delay_between_batches = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="Задержка между пакетами (сек)",
        help_text="Пауза между обработкой разных пакетов",
    )
    max_retry_attempts = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Макс. число попыток",
        help_text="Максимальное количество попыток отправки сообщения",
    )
    cleanup_age_days = models.PositiveSmallIntegerField(
        default=30,
        verbose_name="Дни до очистки",
        help_text="Максимальное количество дней по хранению старых записей",
    )

    class Meta:
        verbose_name = "Настройки Молнии"
        verbose_name_plural = "Настройки молний"

    def __str__(self):
        return "Настройки молний"

    @property
    def active_days(self):
        """Возвращает список активных дней недели (0 = понедельник, 6 = воскресенье)"""
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
