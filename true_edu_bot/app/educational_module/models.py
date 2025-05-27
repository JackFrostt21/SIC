from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from rest_framework.response import Response
from ckeditor.fields import RichTextField
from django.urls import reverse
from colorfield.fields import ColorField
from solo.models import SingletonModel
import os
import zipfile
import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.exceptions import ValidationError 
import json

from app.core.abstract_models import BaseModel

from django.db.models.signals import post_save, post_delete
from app.core.mixins import ChangeLoggableMixin
from app.core.signals import journal_save_handler, journal_delete_handler


class TagCourse(models.Model):
    tag_name = models.CharField(max_length=255, verbose_name='Наименование тега')

    def __str__(self):
        return self.tag_name
    
    class Meta:
        verbose_name = "Тег программы"
        verbose_name_plural = "Теги программ"


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
    tag = models.ManyToManyField(TagCourse, blank=True, verbose_name='Тэги')
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
        verbose_name = "Программа обучения"
        verbose_name_plural = "Программы обучения"
        ordering = ["id"]


class CourseTopic(BaseModel, ChangeLoggableMixin):
    training_course = models.ForeignKey(
        TrainingCourse,
        related_name="course_topics",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name=_("training_course"),
    )
    title = models.CharField(
        max_length=15, null=True, blank=True, verbose_name=_("Заголовок")
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
        upload_to="Course_Topic/pdf",
        null=True,
        blank=True,
        verbose_name=_("PDF файл для курса"),
    )
    audio_file = models.FileField(
        upload_to="Course_Topic/audio",
        null=True,
        blank=True,
        verbose_name=_("Аудио файл для курса"),
    )
    video_file = models.FileField(
        upload_to="Course_Topic/video",
        null=True,
        blank=True,
        verbose_name=_("Видео файл для курса"),
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
    audio_file_readuser = models.BooleanField(
        default=False, verbose_name=_("Отображать аудио файл в ТГ")
    )
    video_file_readuser = models.BooleanField(
        default=False, verbose_name=_("Отображать видео файл в ТГ")
    )

    class Meta:
        verbose_name = "Тема программы обучения"
        verbose_name_plural = "Темы программы обучения"
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
        verbose_name = "Вопрос по теме"
        verbose_name_plural = "Вопросы по темам"
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
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
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
        upload_to="test_passed",
        null=True,
        blank=True,
        verbose_name=_("Изображение для успешно пройденного теста"),
    )
    image_test_failed = models.ImageField(
        upload_to="test_failed",
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
    spravka_for_bot = RichTextField(null=True, blank=True, verbose_name=_("Описание бота для справки"))
    version_bot = models.TextField(null=True, blank=True, verbose_name=_("Версия бота"))
    image_spravka_for_bot = models.ImageField(
        upload_to="start_images",
        null=True,
        blank=True,
        verbose_name=_("Изображение для справки о боте"),
    )
    image_progess_good = models.ImageField(
        upload_to="test_passed",
        null=True,
        blank=True,
        verbose_name=_("Позитивное изображение для прогресса"),
    )

    image_progess_bad = models.ImageField(
        upload_to="test_failed",
        null=True,
        blank=True,
        verbose_name=_("Негативное изображение для прогресса"),
    )
    certificate = models.FileField(upload_to='start_certificate', blank=True, verbose_name='Сертификат')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ["name"]


def get_namespace(element):
        #извлекаем пространство имен из тега элмента lom
        if element.tag.startswith("{"):
            return element.tag.split("}")[0].strip("{")
        return ""

class ScormPack(models.Model):
    training_course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='scormpack', verbose_name='Программа обучения')
    scorm_file = models.FileField(upload_to='scorm_packs/', verbose_name='SCORM пакет')
    manifest_data = models.JSONField(blank=True, null=True, verbose_name='Манифест для веб')

    def __str__(self):
        return str(self.id)
    
    def clean(self):
        super().clean()
        if self.scorm_file and not self.scorm_file.name.lower().endswith('.zip'):
            raise ValidationError('Неверный формат файла. Нужно загружать ZIP архив.')
        
    #ПЕРЕЗАПИСЫВАТЬ ФАЙЛ ЕСЛИ НАИМЕНОВАНИЕ ИДЕНТИЧНОЕ
    #ПЕРЕЗАПИСЫВАТЬ ФАЙЛ ЕСЛИ НАИМЕНОВАНИЕ ИДЕНТИЧНОЕ
    #ПЕРЕЗАПИСЫВАТЬ ФАЙЛ ЕСЛИ НАИМЕНОВАНИЕ ИДЕНТИЧНОЕ
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # После сохранения выполняем распаковку и парсинг манифеста
        self.extract_and_parse_manifest()   
    
    def extract_and_parse_manifest(self):
        # Получаем путь к архиву SCORM
        zip_path = self.scorm_file.path
        print(f'Путь к архиву: {zip_path}')
        
        # Формируем путь к каталогу для распаковки: MEDIA_ROOT/scorm_extracted/<id>/
        extract_dir = os.path.join(settings.MEDIA_ROOT, 'scorm_extracted', str(self.id))
        print(f'Путь к каталогу курса: {extract_dir}')
        
        # Создаём директорию, если её ещё нет
        os.makedirs(extract_dir, exist_ok=True)

        # Распаковка архива
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except Exception as e:
            print(f'Ошибка при распаковке архива: {e}')
            return

        print(f'Архив распакован в {extract_dir}')

        # Ищем файл imsmanifest.xml в корне каталога
        manifest_path = os.path.join(extract_dir, 'imsmanifest.xml')
        print(f'Проверяем наличие манифеста в корне: {manifest_path}')
        
        if not os.path.exists(manifest_path):
            # Если манифест не найден в корне, выполняем рекурсивный поиск
            for root_dir, dirs, files in os.walk(extract_dir):
                if 'imsmanifest.xml' in files:
                    manifest_path = os.path.join(root_dir, 'imsmanifest.xml')
                    print(f'Манифест найден не в корне, по пути: {manifest_path}')
                    break

        # Если манифест найден, считываем его содержание
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, encoding='utf-8') as f:
                    manifest_content = f.read()
                print('Содержимое манифеста успешно считано.')
                # Сохраняем сырой текст манифеста в поле manifest_data
                self.manifest_data = manifest_content
                # Обновляем объект в базе без повторного вызова save() (чтобы избежать рекурсии)
                ScormPack.objects.filter(pk=self.pk).update(manifest_data=manifest_content)
            except Exception as e:
                print(f'Ошибка при чтении манифеста: {e}')
        else:
            # Если манифест не найден, сохраняем сообщение об ошибке в manifest_data
            self.manifest_data = {"error": "Манифест не найден"}
            ScormPack.objects.filter(pk=self.pk).update(manifest_data=self.manifest_data)
            print('Манифест не найден')

    class Meta:
        verbose_name = "SCORM пакет"
        verbose_name_plural = "SCORM пакеты"


class NewsBlock(models.Model):
    news_title = models.CharField(max_length=100, verbose_name='Наименование', default='Новости')
    start_date_news = models.DateField(verbose_name='Дата старта новости')
    end_date_news = models.DateField(null=True, blank=True, verbose_name='Дата завершения новости')
    text_news = RichTextField(null=True, blank=True, verbose_name=_('Текст новости'))

    def __str__(self):
        return 'Новости'
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"


class Certificate(models.Model):
    user = models.ForeignKey("bot.TelegramUser", on_delete=models.DO_NOTHING, related_name='certificates', verbose_name='Студент')
    training_course_certificate = models.ForeignKey(TrainingCourse, on_delete=models.DO_NOTHING, related_name='certificates', verbose_name='Программа обучения')
    result = models.IntegerField(verbose_name='Результат')
    certificate_file = models.FileField(upload_to='certificates/', verbose_name='Адрес файла', blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Сертификат {self.user} по курсу {self.training_course_certificate}"
    
    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'


class RatingTrainingCourse(models.Model):
    training_course = models.ForeignKey(TrainingCourse, on_delete=models.DO_NOTHING, verbose_name='Программа обучения', related_name='rating_course')
    student = models.ForeignKey('bot.TelegramUser', on_delete=models.DO_NOTHING, verbose_name='Студент')
    rating = models.IntegerField(blank=True, verbose_name='Оценка')

    def __str__(self):
        return f'Рейтинг по программе обучения {self.training_course}'
    
    class Meta:
        verbose_name = 'Рейтинг программы'
        verbose_name_plural = 'Рейтинги программ'


class CourseDeadline(models.Model):
    deadline_date = models.DateField(verbose_name='Дата дедлайна')
    training_course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='deadlines', verbose_name='Программа обучения')
    deadline_groups = models.ManyToManyField("bot.TelegramGroup", blank=True, related_name='deadlines', verbose_name='Группы')
    deadline_telegramusers = models.ManyToManyField("bot.TelegramUser", blank=True, related_name='deadlines', verbose_name='Студенты')

    class Meta:
        verbose_name = 'Дедлайн'
        verbose_name_plural = 'Дедлайны'

    def __str__(self):
        return f'Дедлайн для {self.training_course}'


class RegistrationSetting(SingletonModel):
    regbot_work = models.BooleanField(verbose_name='Включить RegBot', default=False)
    url_regbot = models.URLField(verbose_name='URL для API')
    bot_reg_url = models.URLField(verbose_name='Ссылка на бота регистрации', null=True, blank=True)
    
    def __str__(self):
        return 'Настройки регистрации'

    class Meta:
        verbose_name = 'Настройки регистрации'


def log_active(model_list):
    for m in model_list:
        post_save.connect(journal_save_handler, sender=m)
        post_delete.connect(journal_delete_handler, sender=m)


log_active(
    [TrainingCourse, CourseTopic, Subtopic, TopicQuestion, AnswerOption, Company, CourseDirection]
)
