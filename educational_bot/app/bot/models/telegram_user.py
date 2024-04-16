from django.db import models
from django.db.models.signals import post_save, post_delete

from app.core.abstract_models import BaseRowStateModel
from app.core.mixins import ChangeLoggableMixin
from app.core.models import BaseModel
from app.core.signals import journal_save_handler, journal_delete_handler


class TelegramUser(BaseModel, BaseRowStateModel, ChangeLoggableMixin):
    user_id = models.BigIntegerField(verbose_name='user_id', unique=True)
    user_name = models.CharField(max_length=100, verbose_name='user_name', blank=True, null=True)
    full_name = models.CharField(max_length=100, verbose_name='full_name', blank=True, null=True)
    date_of_birth = models.CharField(max_length=100, verbose_name='date_of_birth', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='phone', blank=True, null=True, unique=True)
    language = models.CharField(max_length=20, verbose_name='language', blank=True, null=True)
    tg_mention = models.CharField(max_length=100, verbose_name='tg_mention', blank=True, null=True)
    testing_process = models.BooleanField(default=False, verbose_name='testing_process')
    RATING_CHOICES = (
        ("CHAMPION", "champion"),
        ("MASTER", "master"),
        ("EXPERT", "expert"),
        ("BEGINNER", "beginner"),
        ("STUDENT", "student"),
        ("RESEARCHER", "researcher")
    )
    rating = models.CharField(max_length=150, choices=RATING_CHOICES, default="BEGINNER")
    current_question_index = models.PositiveSmallIntegerField(default=1)


    def save(self, *args, **kwargs):
        try:
            super(TelegramUser, self).save(*args, **kwargs)
        except Exception as e:
            print(e)

    class Meta:
        verbose_name = 'TelegramUser'
        verbose_name_plural = "TelegramUser's"
        ordering = ['id']

    def __str__(self):

        if self.user_name is None:
            logo = f'{self.phone}'
        else:
            logo = f' {self.user_name} | {self.phone}'

        return logo


# class UserRating(BaseModel):
#     LEVEL_CHOICE = (
#         ("champion", "Champion"),
#         ("master", "Master"),
#         ("expert", "Expert"),
#         ("beginner", "Beginner"),
#         ("student", "Student"),
#         ("explorer", "Explorer"),
#     )
#     user = models.OneToOneField(to='testing_module.TelegramUser', on_delete=models.DO_NOTHING, null=True, blank=True)
#     level = models.CharField(max_length=50, choices=LEVEL_CHOICE, null=True, blank=True)

#     @classmethod
#     def get_rating(cls):
#         quantity_champion = cls.objects.filter(level='champion').count()
#         quantity_master = cls.objects.filter(level='master').count()
#         quantity_expert = cls.objects.filter(level='expert').count()
#         quantity_beginner = cls.objects.filter(level='beginner').count()
#         quantity_student = cls.objects.filter(level='student').count()
#         quantity_explorer = cls.objects.filter(level='explorer').count()
#         return quantity_champion, quantity_master, quantity_expert, quantity_beginner, quantity_student, quantity_explorer

def log_active(model_list):
    for m in model_list:
        post_save.connect(journal_save_handler, sender=m)
        post_delete.connect(journal_delete_handler, sender=m)


log_active([TelegramUser])
