from django.db import models

from django_ckeditor_5.fields import CKEditor5Field

from app.core.abstract_models import BaseModel
from .courses import TrainingCourse
from ...organization.models import Department, JobTitle


class Certificate(BaseModel):
    """
    Сертификат о прохождении курса
    """

    user = models.ForeignKey(
        "bot.TelegramUser",
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="Студент",
    )
    training_course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="Программа обучения",
    )
    recipient_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="ФИО получателя",
    )
    course_title = models.CharField(
        max_length=400,
        blank=True,
        default="",
        verbose_name="Название курса",
    )
    result = models.IntegerField(verbose_name="Результат")
    completed_at = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата успешного прохождения",
    )
    expires_at = models.DateField(
        null=True,
        blank=True,
        verbose_name="Действителен до",
    )
    certificate_file = models.FileField(
        upload_to="certificates/", verbose_name="Файл сертификата", blank=True
    )

    def __str__(self):
        return f"{self.user} - {self.training_course} - {self.result}%"

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "training_course"],
                name="uniq_certificate_user_course",
            ),
            models.CheckConstraint(
                check=models.Q(result__gte=0, result__lte=100),
                name="certificate_result_between_0_and_100",
            ),
        ]


class RatingTrainingCourse(BaseModel):
    """
    Рейтинг программы обучения
    """

    training_course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        verbose_name="Программа обучения",
        related_name="rating_course",
    )
    student = models.ForeignKey(
        "bot.TelegramUser", on_delete=models.CASCADE, verbose_name="Студент"
    )
    rating = models.IntegerField(verbose_name="Оценка")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    def __str__(self):
        return f"{self.student} - {self.training_course} - {self.rating}"

    class Meta:
        verbose_name = "Рейтинг программы"
        verbose_name_plural = "Рейтинги программ"


class CourseDeadline(BaseModel):
    """
    Дедлайн для программы обучения
    """

    deadline_date = models.DateField(verbose_name="Дата дедлайна")
    training_course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        related_name="deadlines",
        verbose_name="Программа обучения",
    )
    deadline_groups = models.ManyToManyField(
        "bot.TelegramGroup", blank=True, related_name="deadlines", verbose_name="Группы"
    )
    deadline_users = models.ManyToManyField(
        "bot.TelegramUser",
        blank=True,
        related_name="deadlines",
        verbose_name="Студенты",
    )

    class Meta:
        verbose_name = "Дедлайн"
        verbose_name_plural = "Дедлайны"

    def __str__(self):
        return f"{self.training_course} - {self.deadline_date}"


class NewsBlock(BaseModel):
    """
    Новостной блок
    """

    news_title = models.CharField(
        max_length=100, verbose_name="Наименование", default="Новость"
    )
    start_date_news = models.DateField(verbose_name="Дата публикации")
    is_important = models.BooleanField(default=False, verbose_name="Важное")
    text_news = CKEditor5Field(
        config_name="default", null=True, blank=True, verbose_name="Текст новости"
    )

    """НЕ ИСПОЛЬЗУЕТСЯ"""
    end_date_news = models.DateField(
        null=True, blank=True, verbose_name="Дата завершения новости"
    )
    image = models.ImageField(
        upload_to="news", null=True, blank=True, verbose_name="Изображение новости"
    )
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    """НЕ ИСПОЛЬЗУЕТСЯ"""

    def __str__(self):
        return self.news_title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-start_date_news"]


class UserNewsStatus(BaseModel):
    """
    Статус прочтения новости пользователем
    """

    user = models.ForeignKey(
        "bot.TelegramUser", on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    news = models.ForeignKey(
        NewsBlock, on_delete=models.CASCADE, verbose_name="Новость"
    )
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    is_pinned = models.BooleanField(default=False, verbose_name="Закреплено")

    def __str__(self):
        return f"{self.user.user_name} - {self.news.news_title}"

    class Meta:
        verbose_name = "Статус прочтения новости"
        verbose_name_plural = "Статусы прочтения новостей"
        unique_together = ("user", "news")


class ObligatoryList(BaseModel):
    """
    Список обязательных курсов
    """

    training_course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        verbose_name="Программа обучения",
        related_name="obligatory_list",
    )
    department = models.ManyToManyField(
        Department, blank=True, verbose_name="Подразделения"
    )
    jobtitle = models.ManyToManyField(JobTitle, blank=True, verbose_name="Должности")

    class Meta:
        verbose_name = "Список обязательных курсов"
        verbose_name_plural = "Списки обязательных курсов"

    def __str__(self):
        return f"Обязательный курс: {self.training_course.title}"


class CourseAssignmentNotification(BaseModel):
    """
    История отправленных уведомлений о назначении курсов пользователям
    """

    training_course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        verbose_name="Программа обучения",
        related_name="assignment_notifications",
    )
    user = models.ForeignKey(
        "bot.TelegramUser",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="course_assignment_notifications",
    )
    notified_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время уведомления"
    )

    class Meta:
        verbose_name = "Уведомление о назначении курса"
        verbose_name_plural = "Уведомления о назначении курсов"
        unique_together = ("training_course", "user")
        ordering = ["-notified_at"]
        indexes = [
            models.Index(fields=["training_course", "user"]),
            models.Index(fields=["-notified_at"]),
        ]

    def __str__(self):
        user_name = (
            self.user.full_name or self.user.user_name or f"ID: {self.user.telegram_id}"
        )
        return f"{self.training_course.title} → {user_name}"
