import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from app.bot.models.telegram_user import CustomUser


class PasswordResetToken(models.Model):
    """
    Модель для токенов сброса пароля.
    Каждый токен имеет ограниченное время жизни и может быть использован только один раз.
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="password_reset_tokens",
    )
    token = models.CharField(max_length=255, unique=True, verbose_name="Токен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    expires_at = models.DateTimeField(verbose_name="Дата истечения")
    is_used = models.BooleanField(default=False, verbose_name="Использован")
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP адрес"
    )

    class Meta:
        verbose_name = "Токен сброса пароля"
        verbose_name_plural = "Токены сброса пароля"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user", "is_used"]),
            models.Index(fields=["expires_at"]),
        ]

    def save(self, *args, **kwargs):
        # Генерируем уникальный токен при создании
        if not self.token:
            self.token = self.generate_token()

        # Устанавливаем время истечения (1 час от создания)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)

        super().save(*args, **kwargs)

    @staticmethod
    def generate_token():
        """Генерирует уникальный токен"""
        return str(uuid.uuid4()).replace("-", "")

    def is_valid(self):
        """
        Проверяет валидность токена:
        - не использован
        - не истек
        """
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Помечает токен как использованный"""
        self.is_used = True
        self.save(update_fields=["is_used"])

    def time_until_expiry(self):
        """Возвращает оставшееся время до истечения"""
        if timezone.now() >= self.expires_at:
            return timedelta(0)
        return self.expires_at - timezone.now()

    @classmethod
    def invalidate_user_tokens(cls, user):
        """Помечает все активные токены пользователя как использованные"""
        cls.objects.filter(
            user=user, is_used=False, expires_at__gt=timezone.now()
        ).update(is_used=True)

    @classmethod
    def cleanup_expired_tokens(cls):
        """Удаляет истекшие токены (для ручного вызова)"""
        expired_count = cls.objects.filter(expires_at__lt=timezone.now()).count()

        cls.objects.filter(expires_at__lt=timezone.now()).delete()

        return expired_count

    def __str__(self):
        status = "использован" if self.is_used else "активен"
        return f"Токен для {self.user.username} ({status})"
