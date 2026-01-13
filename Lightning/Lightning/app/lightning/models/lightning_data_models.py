from django.db import models
from app.lightning.models.lightning_models import Lightning


class LightningRead(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="Прочитано"
    )
    updated_at = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="Обновлено"
    )
    user = models.ForeignKey(
        "bot.TelegramUser", on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    lightning = models.ForeignKey(
        Lightning, on_delete=models.CASCADE, verbose_name="Молния"
    )
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Статус чтения молнии"
        verbose_name_plural = "Статусы чтения молний"
        ordering = ["created_at"]
        unique_together = ("user", "lightning")


class LightningTest(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="Дата записи теста"
    )
    updated_at = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="Обновление записи теста"
    )
    user = models.ForeignKey(
        "bot.TelegramUser", on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    lightning = models.ForeignKey(
        Lightning, on_delete=models.CASCADE, verbose_name="Молния"
    )
    complete = models.BooleanField(default=False, verbose_name="Успешно")
    quantity_correct = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Процент правильных ответов"
    )
    quantity_not_correct = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Процент не правильных ответов"
    )

    class Meta:
        verbose_name = "Результат тестирования"
        verbose_name_plural = "Результаты тестирования"
        ordering = ["created_at"]
        unique_together = ("user", "lightning")

    def __str__(self):
        return f"{self.user} |{self.lightning} | {self.complete} |"