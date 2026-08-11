from django.db.models.signals import post_save, post_delete
from django.db import transaction
from django.dispatch import receiver

from app.bot.models.education_data import UserTest
from app.bot.models.rating import UserRating


def _recalc_user_rating_async(user):
    """Пересчёт рейтинга пользователя после коммита транзакции."""
    try:
        UserRating.recalc_for_user(user)
    except Exception:
        # Предотвращаем падение сигнала;
        pass


@receiver(post_save, sender=UserTest)
def usertest_post_save(sender, instance, **kwargs):
    user = instance.user
    if not user:
        return
    transaction.on_commit(lambda: _recalc_user_rating_async(user))


@receiver(post_delete, sender=UserTest)
def usertest_post_delete(sender, instance, **kwargs):
    user = instance.user
    if not user:
        return
    transaction.on_commit(lambda: _recalc_user_rating_async(user))
