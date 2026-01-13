from django.db import models
from app.organization.models.company_models import Company

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