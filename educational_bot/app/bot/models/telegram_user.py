from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import gettext as _
from app.educational_module.models import Company, TrainingCourse, CourseTopic
import re

from app.core.abstract_models import BaseRowStateModel
from app.core.mixins import ChangeLoggableMixin
from app.core.models import BaseModel
from app.core.signals import journal_save_handler, journal_delete_handler


class TelegramUser(BaseModel, BaseRowStateModel, ChangeLoggableMixin):
    user_id = models.BigIntegerField(verbose_name="Telegram ID пользователя", unique=True)
    user_name = models.CharField(
        max_length=100, verbose_name="Telegram имя пользователя ", blank=True, null=True
    )
    full_name = models.CharField(
        max_length=100, verbose_name="ФИО", blank=True, null=True
    )
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", blank=True, null=True)
    first_name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    middle_name = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    date_of_birth = models.CharField(
        max_length=100, verbose_name="Дата рождения", blank=True, null=True
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон", blank=True, null=True, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('Компания'),null=True, blank=True)
    language = models.CharField(
        max_length=20, verbose_name="Язык", blank=True, null=True
    )
    tg_mention = models.CharField(
        max_length=100, verbose_name="tg_mention", blank=True, null=True
    )
    testing_process = models.BooleanField(default=False, verbose_name="testing_process")
    current_question_index = models.PositiveSmallIntegerField(default=1)

    # def save(self, *args, **kwargs):
    #     try:
    #         super(TelegramUser, self).save(*args, **kwargs)
    #     except Exception as e:
    #         print(e)

    def save(self, *args, **kwargs):
        if self.full_name:  # Проверяем, что full_name не пустое и не None
            self.last_name, self.first_name, self.middle_name = self.parse_full_name(self.full_name)
        
        # В любом случае сохраняем объект, даже если full_name пустое
        super().save(*args, **kwargs)

    @staticmethod
    def parse_full_name(full_name):
        name_parts = re.split(r'\s+', full_name.strip())

        if len(name_parts) == 1:
            return name_parts[0], '', ''  # Только фамилия
        elif len(name_parts) == 2:
            return name_parts[0], name_parts[1], ''  # Фамилия и имя
        elif len(name_parts) >= 3:
            return name_parts[0], name_parts[1], ' '.join(name_parts[2:])  # Фамилия, имя и отчество
        else:
            return '', '', ''  # В случае ошибки

    class Meta:
        verbose_name = "TelegramUser"
        verbose_name_plural = "TelegramUser's"
        ordering = ["id"]

    def __str__(self):
        return f'{self.full_name} | {self.user_name}'


class TelegramGroup(ChangeLoggableMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование группы")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    users = models.ManyToManyField(TelegramUser, blank=True, related_name="Пользователи")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "TelegramGroup"
        verbose_name_plural = "TelegramGroups"
        ordering = ["name"]


class UserRead(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, verbose_name=_('Курс'))
    topic = models.ForeignKey(CourseTopic, on_delete=models.CASCADE, verbose_name=_('Тема курса'))
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course', 'topic')


###Модель для хранения действий пользователя в ТГ
class UserAction(models.Model):
    user = models.CharField(max_length=100, null=True, blank=True, verbose_name="User")
    action_type = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Type of Action"
    )
    action_details = models.TextField(
        blank=True, null=True, verbose_name="Action Details"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    action_text = models.TextField(blank=True, null=True, verbose_name="Action Text", default="")

    def __str__(self):
        return f"{self.user} - {self.action_type} at {self.timestamp}"

    class Meta:
        verbose_name = "User Action"
        verbose_name_plural = "User Actions"
        ordering = ["-timestamp"]  # Сортировка по убыванию даты


def log_active(model_list):
    for m in model_list:
        post_save.connect(journal_save_handler, sender=m)
        post_delete.connect(journal_delete_handler, sender=m)


log_active([TelegramUser, TelegramGroup])
