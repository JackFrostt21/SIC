from django.core.exceptions import ValidationError
from django.db import models

from app.core.abstract_models import BaseModel
from .telegram_user import TelegramUser
from app.learning_app.models.courses import CourseTopic


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
    course_topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Тема курса",
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
        target = self.training or self.course_topic or "Без привязки"
        return f"{self.user} - {target} - {'Пройден' if self.complete else 'Не пройден'}"

    def clean(self):
        """
        Разрешаем привязку либо к курсу, либо к теме, либо черновик без привязки.
        Оба одновременно — ошибка.
        """
        if self.training and self.course_topic:
            raise ValidationError(
                {"course_topic": "Укажите либо курс, либо тему, но не оба сразу."}
            )
        return super().clean()
    
