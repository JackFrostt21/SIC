from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from rest_framework.response import Response
from ckeditor.fields import RichTextField
from django.urls import reverse
from colorfield.fields import ColorField

from app.core.abstract_models import BaseModel
# from users.models import CustomUser

from django.db.models.signals import post_save, post_delete
from app.core.mixins import ChangeLoggableMixin
from app.core.signals import journal_save_handler, journal_delete_handler


class CourseDirection(models.Model):
    title = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Название"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Описание")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Направление программы обучения"
        verbose_name_plural = "Направления программ обучения"
        ordering = ["title"]


class TrainingCourse(BaseModel, ChangeLoggableMixin):
    archive = models.BooleanField(verbose_name='Архивный', default=False)
    title = models.CharField(
        max_length=400, null=True, blank=True, verbose_name=_("Заголовок")
    )
    course_direction = models.ForeignKey(
        CourseDirection,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Направление программы обучения",
    )
    # author = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name='Автор')
    author = models.CharField(max_length=100, null=True, blank=True, verbose_name='Автор')
    description = models.TextField(null=True, blank=True, verbose_name=_("Описание"))
    min_test_percent_course = models.IntegerField(
        default=90,
        null=False,
        blank=False,
        verbose_name=_("Минимальный процент для прохождения курса"),
    )
    user = models.ManyToManyField(
        "bot.TelegramUser", blank=True, verbose_name=_("Пользователь")
    )
    group = models.ManyToManyField(
        "bot.TelegramGroup",
        blank=True,
        verbose_name=_("Группа пользователей"),
    )
    image_course = models.ImageField(
        upload_to="training_course",
        null=True,
        blank=True,
        verbose_name=_("Изображение для курса"),
    )

    def __str__(self):
        if self.title:
            name = self.title
        else:
            name = self.id
        return name

    class Meta:
        verbose_name = _("TrainingCourse")
        verbose_name_plural = _("TrainingCourses")
        ordering = ["id"]


class CourseTopic(BaseModel, ChangeLoggableMixin):
    title = models.CharField(
        max_length=13, null=True, blank=True, verbose_name=_("Заголовок")
    )
    description = models.TextField(null=True, blank=True, verbose_name=_("Описание"))
    main_text = RichTextField(null=True, blank=True, verbose_name=_("Основной текст"))
    image_course_topic = models.ImageField(
        upload_to="Course_Topic",
        null=True,
        blank=True,
        verbose_name=_("Изображение для темы курса"),
    )
    pdf_file = models.FileField(
        upload_to="Course_Topic",
        null=True,
        blank=True,
        verbose_name=_("PDF файл для курса"),
    )
    training_course = models.ForeignKey(
        TrainingCourse,
        related_name="course_topics",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name=_("training_course"),
    )
    main_text_readuser = models.BooleanField(
        default=False, verbose_name=_("Отображать основной текст в ТГ")
    )
    main_text_webapp_readuser = models.BooleanField(
        default=False, verbose_name=_("Отображать основной текст в ТГ в формате WebApp")
    )
    pdf_file_readuser = models.BooleanField(
        default=False, verbose_name=_("Отображать PDF файл в ТГ")
    )

    class Meta:
        verbose_name = _("CourseTopic")
        verbose_name_plural = _("CourseTopics")
        ordering = ["training_course", "id"]

    def get_pdf_url(self):
        return reverse("course_topic_pdf", kwargs={"pk": self.pk})

    def __str__(self):
        if self.title:
            name = f"{self.training_course} | {self.title}"
        else:
            name = self.id
        return name

    def more_info(self):
        return mark_safe(
            f"""                                                   
<a href='/educational_module/coursetopic/{self.id}/change/'> Перейти для редактирования: {self.id} </a>
    """
        )

    more_info.short_description = _("more_info")


class Subtopic(BaseModel, ChangeLoggableMixin):
    title = models.CharField(
        max_length=500, null=True, blank=True, verbose_name=_("title")
    )
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))
    main_text = models.TextField(null=True, blank=True, verbose_name=_("main_text"))
    course_topic = models.ForeignKey(
        CourseTopic,
        related_name="topic_subtopic",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name=_("course_topic"),
    )

    class Meta:
        verbose_name = _("Subtopic")
        verbose_name_plural = _("Subtopics")
        ordering = ["course_topic", "id"]

    def __str__(self):
        if self.title:
            name = f"{self.course_topic} | {self.title}"
        else:
            name = self.id
        return name


class TopicQuestion(BaseModel, ChangeLoggableMixin):
    title = models.CharField(
        max_length=500, null=True, blank=True, verbose_name=_("title")
    )
    # topic = models.ForeignKey(CourseTopic, on_delete=models.DO_NOTHING, null=True, blank=True,
    #                           related_name="topic_questions", verbose_name=_("topic"))
    training = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("course"),
    )
    is_multiple_choice = models.BooleanField(
        default=False, verbose_name="Несколько ответов"
    )
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = _("TopicQuestion")
        verbose_name_plural = _("TopicQuestions")
        ordering = ["training"]

    def __str__(self):
        if self.title:
            name = f"{self.training} | {self.title}"
        else:
            name = self.id
        return name

    def more_info(self):
        return mark_safe(
            f"""                                                   
<a href='/educational_module/topicquestion/{self.id}/change/'> Перейти для редактирования: {self.id} </a>
        """
        )

    more_info.short_description = _("more_info")


class AnswerOption(BaseModel, ChangeLoggableMixin):
    topic_question = models.ForeignKey(
        TopicQuestion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("topic_question"),
        related_name="answer_options",
    )
    number = models.CharField(
        max_length=5, null=True, blank=True, verbose_name=_("number")
    )
    text = models.TextField(null=True, blank=True, verbose_name=_("text"))
    is_correct = models.BooleanField(default=False, verbose_name=_("is_correct"))

    class Meta:
        verbose_name = _("AnswerOption")
        verbose_name_plural = _("AnswerOptions")
        ordering = ["id", "number"]

    def __str__(self):
        if self.topic_question:
            name = f"{self.topic_question} | {self.number}"
        else:
            name = self.id
        return name


class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Наименование"))
    logo_company = models.ImageField(
        upload_to="company", null=True, blank=True, verbose_name=_("Логотип компании")
    )
    color_theme_company = ColorField(
        default="#4a8bed", verbose_name=_("Основной цвет компании")
    )
    image_start_company = models.ImageField(
        upload_to="start_images",
        null=True,
        blank=True,
        verbose_name=_("Стартовое изображение для ТГ"),
    )
    image_list_courses = models.ImageField(
        upload_to="list_courses",
        null=True,
        blank=True,
        verbose_name=_("Изображение для списка курсов в ТГ"),
    )
    image_list_settings = models.ImageField(
        upload_to="list_settings",
        null=True,
        blank=True,
        verbose_name=_("Изображение для настроек в ТГ"),
    )
    image_progress = models.ImageField(
        upload_to="image_progress",
        null=True,
        blank=True,
        verbose_name=_("Изображение для прогресса в ТГ"),
    )
    image_test_passed = models.ImageField(
        upload_to="test passed",
        null=True,
        blank=True,
        verbose_name=_("Изображение для успешно пройденного теста"),
    )
    image_test_failed = models.ImageField(
        upload_to="test failed",
        null=True,
        blank=True,
        verbose_name=_("Изображение для неудачно пройденного теста"),
    )
    image_test_start = models.ImageField(
        upload_to="start_images",
        null=True,
        blank=True,
        verbose_name=_("Стартовое изображение для теста"),
    )
    spravka_for_bot = models.TextField(
        null=True, blank=True, verbose_name=_("Описание бота для справки")
    )
    version_bot = models.TextField(null=True, blank=True, verbose_name=_("Версия бота"))
    image_spravka_for_bot = models.ImageField(
        upload_to="start_images",
        null=True,
        blank=True,
        verbose_name=_("Изображение для справки о боте"),
    )
    image_progess_good = models.ImageField(
        upload_to="test passed",
        null=True,
        blank=True,
        verbose_name=_("Позитивное изображение для прогресса"),
    )

    image_progess_bad = models.ImageField(
        upload_to="test failed",
        null=True,
        blank=True,
        verbose_name=_("Негативное изображение для прогресса"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        ordering = ["name"]


def log_active(model_list):
    for m in model_list:
        post_save.connect(journal_save_handler, sender=m)
        post_delete.connect(journal_delete_handler, sender=m)


log_active(
    [TrainingCourse, CourseTopic, Subtopic, TopicQuestion, AnswerOption, Company, CourseDirection]
)
