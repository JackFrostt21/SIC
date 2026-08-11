from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import mark_safe

from app.core.abstract_models import BaseModel
from app.core.mixins import OrderableMixin
from .courses import TrainingCourse, CourseTopic


class TopicQuestion(BaseModel, OrderableMixin):
    """
    Вопрос для тестирования
    """
    title = models.CharField(max_length=500, verbose_name="Текст вопроса")
    training = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Программа обучения",
        related_name="questions",
    )
    course_topic = models.ForeignKey(
        CourseTopic,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Тема курса",
        related_name="questions",
    )
    is_multiple_choice = models.BooleanField(
        default=False, 
        verbose_name="Несколько вариантов ответа"
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["training", "order"]

    def __str__(self):
        target = (
            self.training.title
            if self.training
            else (self.course_topic.title if self.course_topic else "Без привязки")
        )
        return f"{target} | Вопрос {self.order or '-'}"

    def clean(self):
        """
        Запрещаем одновременную привязку и к курсу, и к теме.
        Черновики без привязки допускаем.
        """
        if self.training and self.course_topic:
            raise ValidationError(
                {"course_topic": "Укажите либо курс, либо тему, но не оба сразу."}
            )
        return super().clean()

    def more_info(self):
        return mark_safe(
            f"""                                                   
<a href='/admin/learning_app/topicquestion/{self.id}/change/'> Перейти для редактирования: {self.id} </a>
    """
        )

    more_info.short_description = "More Info"


class AnswerOption(BaseModel, OrderableMixin):
    """
    Вариант ответа на вопрос
    """
    topic_question = models.ForeignKey(
        TopicQuestion,
        on_delete=models.CASCADE,
        verbose_name="Вопрос",
        related_name="answer_options",
    )
    text = models.TextField(verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"
        ordering = ["topic_question", "order"]

    def __str__(self):
        return f"{self.topic_question} | Ответ {self.order}"
