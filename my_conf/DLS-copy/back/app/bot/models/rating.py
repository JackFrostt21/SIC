from django.db import models
from app.core.abstract_models import BaseModel
from app.bot.models.telegram_user import TelegramUser

class UserRating(BaseModel):
    """
    Рейтинг пользователя
    """
    user = models.OneToOneField(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name='Пользователь'
    )
    points = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество баллов',
        db_index=True
    )

    class Meta:
        verbose_name = 'Рейтинг пользователя'
        verbose_name_plural = 'Рейтинг пользователей'
        ordering = ['-points', 'user_id']

    def __str__(self):
        return f'{self.user} — {self.points} баллов'

    @classmethod
    def recalc_for_user(cls, user):
        from django.db.models import Sum
        from app.bot.models.education_data import UserTest
        total = UserTest.objects.filter(user=user).aggregate(total=Sum('quantity_correct'))['total'] or 0
        obj, _ = cls.objects.update_or_create(user=user, defaults={'points': total})
        return obj