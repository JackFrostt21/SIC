from django.db import models
from django_ckeditor_5.fields import CKEditor5Field 

from app.core.abstract_models import BaseModel


class Company(BaseModel):
    """
    Модель компании
    """
    name = models.CharField(max_length=100, verbose_name="Наименование")
    logo = models.ImageField(
        upload_to="company", 
        null=True, 
        blank=True, 
        verbose_name="Логотип компании"
    )
    
    # Шаблон сертификата
    certificate_template = models.FileField(
        upload_to='company/certificate', 
        blank=True, 
        null=True,
        verbose_name='Шаблон сертификата'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ["name"]


class SettingsBot(BaseModel):
    """
    Настройки бота
    """
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        verbose_name='Компания')
    
    # Изображения для разных состояний бота
    image_start = models.ImageField(
        upload_to="company/start_images",
        null=True,
        blank=True,
        verbose_name="Стартовое изображение для ТГ",
    )
    image_list_courses = models.ImageField(
        upload_to="company/list_courses",
        null=True,
        blank=True,
        verbose_name="Изображение для списка курсов в ТГ",
    )
    image_settings = models.ImageField(
        upload_to="company/list_settings",
        null=True,
        blank=True,
        verbose_name="Изображение для настроек в ТГ",
    )
    image_progress = models.ImageField(
        upload_to="company/image_progress",
        null=True,
        blank=True,
        verbose_name="Изображение для прогресса в ТГ",
    )
    image_test_passed = models.ImageField(
        upload_to="company/test_passed",
        null=True,
        blank=True,
        verbose_name="Изображение для успешно пройденного теста",
    )
    image_test_failed = models.ImageField(
        upload_to="company/test_failed",
        null=True,
        blank=True,
        verbose_name="Изображение для неудачно пройденного теста",
    )
    image_test_start = models.ImageField(
        upload_to="company/start_images",
        null=True,
        blank=True,
        verbose_name="Стартовое изображение для теста",
    )
    
    # Справочная информация
    bot_help_text = CKEditor5Field(
        config_name='default', 
        null=True, 
        blank=True, 
        verbose_name="Описание бота для справки"
    )
    bot_version = models.CharField(
        max_length=20,
        null=True, 
        blank=True, 
        verbose_name="Версия бота"
    )
    image_help = models.ImageField(
        upload_to="company/help",
        null=True,
        blank=True,
        verbose_name="Изображение для справки о боте",
    )
    
    # Изображения для прогресса
    image_progress_good = models.ImageField(
        upload_to="company/progress",
        null=True,
        blank=True,
        verbose_name="Позитивное изображение для прогресса",
    )
    image_progress_bad = models.ImageField(
        upload_to="company/progress",
        null=True,
        blank=True,
        verbose_name="Негативное изображение для прогресса",
    )
    url_web_app = models.URLField(
        null=True,
        blank=True,
        verbose_name="URL для WebApp",
    )

    def __str__(self):
        return f"{self.company} - {self.bot_version}"
    
    class Meta:
        verbose_name = "Настройки бота"
        verbose_name_plural = "Настройки ботов"
        ordering = ["company"]


class JobTitle(BaseModel):
    """
    Модель должности
    """
    name = models.CharField(max_length=100, verbose_name='Должность')
    source_id = models.CharField(max_length=100, verbose_name='ГУИД 1С', blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['name']


class Department(BaseModel):
    """
    Модель подразделения
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name='Компания',
    )
    name = models.CharField(max_length=100, verbose_name='Подразделение')
    source_id = models.CharField(max_length=100, verbose_name='ГУИД 1С', blank=True, null=True)
    job_titles = models.ManyToManyField(
        JobTitle, 
        verbose_name='Должности', 
        related_name='departments_of_job_title', 
        blank=True
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Родительское подразделение',
        related_name='children'
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        ordering = ['name']