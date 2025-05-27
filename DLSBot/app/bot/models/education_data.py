from django.db import models

from app.core.abstract_models import BaseModel
from .telegram_user import TelegramUser


class UserRead(BaseModel):
    """
    Модель для отслеживания прочтения материала пользователем
    """
    user = models.ForeignKey(
        TelegramUser, 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        'learning_app.TrainingCourse', 
        on_delete=models.CASCADE, 
        verbose_name='Курс'
    )
    topic = models.ForeignKey(
        'learning_app.CourseTopic', 
        on_delete=models.CASCADE, 
        verbose_name='Тема курса'
    )
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    read_at = models.DateTimeField(auto_now=True, verbose_name='Дата прочтения')

    class Meta:
        verbose_name = "Прочтение материала"
        verbose_name_plural = "Прочтения материалов"
        unique_together = ('user', 'course', 'topic')

    def __str__(self):
        return f"{self.user} - {self.topic} - {'Прочитано' if self.is_read else 'Не прочитано'}"


def default_user_answer():
    return {"results": []}


class UserTest(BaseModel):
    """
    Модель результатов тестирования пользователя
    """
    question = models.ForeignKey(
        "learning_app.TopicQuestion", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Вопрос"
    )
    user = models.ForeignKey(
        TelegramUser, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Пользователь"
    )
    training = models.ForeignKey(
        "learning_app.TrainingCourse", 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        verbose_name="Курс"
    )

    user_answer = models.JSONField(
        verbose_name="Ответы пользователя", 
        default=default_user_answer
    )
    complete = models.BooleanField(
        default=False, 
        verbose_name="Успешно пройден"
    )

    quantity_correct = models.PositiveSmallIntegerField(
        null=True, 
        blank=True, 
        verbose_name="Процент правильных ответов"
    )
    quantity_not_correct = models.PositiveSmallIntegerField(
        null=True, 
        blank=True, 
        verbose_name="Процент неправильных ответов"
    )

    class Meta:
        verbose_name = "Тест пользователя"
        verbose_name_plural = "Тесты пользователей"

    def __str__(self):
        return f"{self.user} - {self.training} - {'Пройден' if self.complete else 'Не пройден'}"
    