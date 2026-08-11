from django.db import models

from app.core.abstract_models import BaseModel
from app.organization.models import Company


class RegistrationSetting(BaseModel):
    """
    Настройки подключения к системе регистрации.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Наименование",
        default="Подключение к системе регистрации",
    )
    telegram_check_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="URL для проверки Telegram ID",
    )
    employee_check_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="URL для проверки ФИО и ДР",
    )
    api_key = models.CharField(
        max_length=255,
        verbose_name="API ключ",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Настройки регистрации"
        verbose_name_plural = "Настройки регистрации"

    def __str__(self):
        return self.name


class APISettings(models.Model):
    api_url = models.URLField(null=True, blank=True, verbose_name="URL API 1С")
    api_username = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="API Username"
    )
    api_password = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="API Password"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Компания",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Настройки API'
        verbose_name_plural = 'Настройки API'
        ordering = ['api_url']

    def __str__(self):
        return self.api_url
