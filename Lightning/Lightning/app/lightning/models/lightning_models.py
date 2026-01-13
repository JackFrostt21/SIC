from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import MinValueValidator, MaxValueValidator
from app.organization.models.company_models import JobTitle, Department


class Lightning(models.Model):
    is_draft = models.BooleanField(default=True, verbose_name="Черновик")
    name = models.CharField(max_length=100, verbose_name="Молния")
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, null=True, verbose_name="Дата"
    )
    min_test_percent_course = models.PositiveSmallIntegerField(
        default=90, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Минимальный процент для прохождения теста"
    )
    user = models.ManyToManyField(
        "bot.TelegramUser", blank=True, verbose_name="Пользователь"
    )
    group = models.ManyToManyField(
        "bot.TelegramGroup", blank=True, verbose_name="Группа пользователей"
    )
    job_titles = models.ManyToManyField(JobTitle, blank=True, verbose_name="Должности")
    department = models.ManyToManyField(
        Department, blank=True, verbose_name="Подразделения"
    )
    content = CKEditor5Field(blank=True, null=True, verbose_name="Контент")
    image = models.ImageField(upload_to='lightning/images/', null=True, blank=True, verbose_name="Изображение")
    file = models.FileField(upload_to='lightning/files/', null=True, blank=True, verbose_name="Файл")

    class Meta:
        verbose_name = "Молния"
        verbose_name_plural = "Молнии"
        ordering = ["name"]

    def __str__(self):
        return self.name
