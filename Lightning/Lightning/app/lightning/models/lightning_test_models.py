from django.db import models
from app.lightning.models.lightning_models import Lightning


class LightningQuestion(models.Model):
    lightning = models.ForeignKey(
        Lightning,
        related_name="questions",
        verbose_name="Молния",
        on_delete=models.CASCADE,
    )
    name = models.TextField(verbose_name="Вопрос")
    is_multiple_choice = models.BooleanField(
        default=False, verbose_name="Несколько ответов"
    )
    order = models.PositiveSmallIntegerField(default=1, verbose_name="Порядок")

    class Meta:
        verbose_name = "Вопрос молнии"
        verbose_name_plural = "Вопросы молнии"
        ordering = ["order"]

    def __str__(self):
        return self.name or f"Вопрос {self.id}"


class LightningAnswer(models.Model):
    question = models.ForeignKey(
        LightningQuestion,
        related_name="answer",
        on_delete=models.CASCADE,
        verbose_name="Вопрос",
    )
    text = models.TextField(verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    order = models.PositiveSmallIntegerField(default=1, verbose_name="Порядок")

    class Meta:
        verbose_name = "Вариант ответа молнии"
        verbose_name_plural = "Варианты ответов молнии"
        ordering = ["order"]

    def __str__(self):
        return f"Ответ {self.order} для {self.question}"
    
    
""" Количество попыток """
class UserTestAttempt(models.Model):
    telegramuser = models.ForeignKey(
        "bot.TelegramUser",
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    lightning = models.ForeignKey(
        Lightning, on_delete=models.CASCADE, verbose_name="Молния"
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Количество попыток"
        verbose_name_plural = "Количество попыток"

        unique_together = ("telegramuser", "lightning")

    def __str__(self):
        return "Количество попыток"