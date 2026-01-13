from django.db import models
from django.utils import timezone
from app.organization.models.company_models import Company, Department, JobTitle
from app.bot.models.abstract_models import RowStateModel
import re


class TelegramUser(RowStateModel):
    telegram_id = models.BigIntegerField(verbose_name="Telegram ID", unique=True)
    guid_1c = models.CharField(max_length=50, null=True, blank=True, verbose_name="Код 1С")
    username = models.CharField(
        max_length=100, verbose_name="Username", blank=True, null=True
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Компания",
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Подразделение",
    )
    job_title = models.ForeignKey(
        JobTitle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Должность",
    )
    full_name = models.CharField(
        max_length=100, verbose_name="ФИО", blank=True, null=True
    )
    last_name = models.CharField(
        max_length=100, verbose_name="Фамилия", blank=True, null=True
    )
    first_name = models.CharField(
        max_length=100, verbose_name="Имя", blank=True, null=True
    )
    middle_name = models.CharField(
        max_length=100, verbose_name="Отчество", blank=True, null=True
    )
    date_of_birth = models.CharField(
        max_length=10, verbose_name="Дата рождения", blank=True, null=True
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон", blank=True, null=True
    )
    email = models.EmailField(
        max_length=50, verbose_name="Email", blank=True, null=True
    )
    language = models.CharField(
        max_length=20, verbose_name="Язык", blank=True, null=True, default="ru"
    )
    image = models.ImageField(
        upload_to="telegramuser",
        null=True,
        blank=True,
        verbose_name="Фото пользователя",
    )
    last_activity = models.DateField(
        verbose_name="Последняя активность",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def save(self, *args, **kwargs):
        # Собираем full_name
        parts = [
            p.strip()
            for p in (self.last_name, self.first_name, self.middle_name)
            if p and p.strip()
        ]
        self.full_name = " ".join(parts) if parts else None

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь молнии"
        verbose_name_plural = "Пользователи молнии"
        ordering = ["id"]

    def __str__(self):
        return self.full_name or self.username or f"ID: {self.telegram_id}"


class TelegramGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование группы")
    users = models.ManyToManyField(
        TelegramUser, blank=True, verbose_name="Пользователи", related_name="groups"
    )

    class Meta:
        verbose_name = "Группа молнии"
        verbose_name_plural = "Группы молний"
        ordering = ["name"]

    def __str__(self):
        return self.name
