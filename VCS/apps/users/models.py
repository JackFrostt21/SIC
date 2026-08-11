from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Пользователь системы контроля проверок ТС.

    Роли назначаются через стандартные группы и permissions Django.
    
    """
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.get_full_name() or self.username
