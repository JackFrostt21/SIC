from django.db import models

from app.core.abstract_models import BaseModel


class RegistrationSetting(BaseModel):
    """
    Настройки интеграции с системой регистрации
    """
    regbot_active = models.BooleanField(verbose_name='Включить бот регистрации', default=False)
    regbot_api_url = models.URLField(verbose_name='URL API для регистрации')
    regbot_telegram_url = models.URLField(verbose_name='Ссылка на бота регистрации', null=True, blank=True)
    api_key = models.CharField(max_length=100, verbose_name='API ключ', blank=True, null=True)
    
    # Дополнительные настройки
    send_welcome_message = models.BooleanField(
        default=True, 
        verbose_name='Отправлять приветственное сообщение'
    )
    welcome_message_text = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Текст приветственного сообщения'
    )
    
    class Meta:
        verbose_name = 'Настройки регистрации'
        verbose_name_plural = 'Настройки регистрации'

    def __str__(self):
        return 'Настройки регистрации'