from django.db import models
from django.utils.safestring import mark_safe
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
import os
import zipfile
from django.core.exceptions import ValidationError
from django.conf import settings

from app.core.abstract_models import BaseModel
from app.core.mixins import OrderableMixin
from django.contrib.auth.models import User


class TagCourse(BaseModel):
    """
    Теги для курсов
    """
    tag_name = models.CharField(max_length=255, verbose_name='Наименование тега')

    def __str__(self):
        return self.tag_name
    
    class Meta:
        verbose_name = "Тег программы"
        verbose_name_plural = "Теги программ"


class CourseDirection(BaseModel):
    """
    Направления программ обучения
    """
    title = models.CharField(max_length=100, verbose_name="Название")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Направление программы обучения"
        verbose_name_plural = "Направления программ обучения"
        ordering = ["title"]


class TrainingCourse(BaseModel):
    """
    Программа обучения (курс)
    """
    archive = models.BooleanField(verbose_name='Архивный', default=False)
    title = models.CharField(max_length=400, verbose_name="Заголовок")
    tag = models.ManyToManyField(TagCourse, blank=True, verbose_name='Тэги')
    course_direction = models.ForeignKey(
        CourseDirection,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Направление программы обучения",
    )
    # TODO: Добавить связку с юзером
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="training_courses",
        verbose_name="Автор"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    min_test_percent_course = models.IntegerField(
        default=90,
        verbose_name="Минимальный процент для прохождения курса",
    )
    user = models.ManyToManyField(
        "bot.TelegramUser", 
        blank=True, 
        verbose_name="Пользователь"
    )
    group = models.ManyToManyField(
        "bot.TelegramGroup",
        blank=True,
        verbose_name="Группа пользователей",
    )
    image_course = models.ImageField(
        upload_to="training_course",
        null=True,
        blank=True,
        verbose_name="Изображение для курса",
    )

    def __str__(self):
        return self.title or f"Course #{self.id}"

    class Meta:
        verbose_name = "Программа обучения"
        verbose_name_plural = "Программы обучения"
        ordering = ["id"]


class CourseTopic(BaseModel, OrderableMixin):
    """
    Тема программы обучения
    """
    training_course = models.ForeignKey(
        TrainingCourse,
        related_name="course_topics",
        on_delete=models.CASCADE,
        verbose_name="Программа обучения",
    )
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    main_text = CKEditor5Field(config_name='default', null=True, blank=True, verbose_name="Основной текст") 
    image_course_topic = models.ImageField(
        upload_to="Course_Topic",
        null=True,
        blank=True,
        verbose_name="Изображение для темы курса",
    )
    pdf_file = models.FileField(
        upload_to="Course_Topic/pdf",
        null=True,
        blank=True,
        verbose_name="PDF файл для курса",
    )
    audio_file = models.FileField(
        upload_to="Course_Topic/audio",
        null=True,
        blank=True,
        verbose_name="Аудио файл для курса",
    )
    video_file = models.FileField(
        upload_to="Course_Topic/video",
        null=True,
        blank=True,
        verbose_name="Видео файл для курса",
    )
    main_text_readuser = models.BooleanField(
        default=False, 
        verbose_name="Отображать основной текст в ТГ"
    )
    main_text_webapp_readuser = models.BooleanField(
        default=False, 
        verbose_name="Отображать основной текст в ТГ в формате WebApp"
    )
    pdf_file_readuser = models.BooleanField(
        default=False, 
        verbose_name="Отображать PDF файл в ТГ"
    )
    audio_file_readuser = models.BooleanField(
        default=False, 
        verbose_name="Отображать аудио файл в ТГ"
    )
    video_file_readuser = models.BooleanField(
        default=False, 
        verbose_name="Отображать видео файл в ТГ"
    )

    class Meta:
        verbose_name = "Тема программы обучения"
        verbose_name_plural = "Темы программы обучения"
        ordering = ["training_course", "id"]

    def get_pdf_url(self):
        return reverse("course_topic_pdf", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.training_course.title} | {self.title}"

    def more_info(self):
        return mark_safe(
            f"""                                                   
<a href='/admin/learning_app/coursetopic/{self.id}/change/'> Перейти для редактирования: {self.id} </a>
    """
        )

    more_info.short_description = "More Info"

# TODO: посмотреть нужно ли
#Функция для извлечения пространства имен из тега элемента lom 
#Используется для парсинга манифеста - посмотреть нужно ли
def get_namespace(element):
        if element.tag.startswith("{"):
            return element.tag.split("}")[0].strip("{")
        return ""


class ScormPack(BaseModel):
    training_course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='scormpack', verbose_name='Программа обучения')
    scorm_file = models.FileField(upload_to='scorm_packs/', verbose_name='SCORM пакет')
    manifest_data = models.JSONField(blank=True, null=True, verbose_name='Манифест для веб')

    def __str__(self):
        return str(self.id)
    
    def clean(self):
        super().clean()
        if self.scorm_file and not self.scorm_file.name.lower().endswith('.zip'):
            raise ValidationError('Неверный формат файла. Нужно загружать ZIP архив.')

    # TODO: Перезаписывать файл если наименование идентичное
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