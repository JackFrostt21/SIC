from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import gettext as _
from app.educational_module.models import Company, TrainingCourse, CourseTopic
import re
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from app.core.abstract_models import BaseRowStateModel
from app.core.mixins import ChangeLoggableMixin
from app.core.models import BaseModel
from app.reference_data.models import JobTitle, Department
from app.core.signals import journal_save_handler, journal_delete_handler


class TelegramUser(BaseModel, BaseRowStateModel, ChangeLoggableMixin):
    user_id = models.BigIntegerField(verbose_name="Telegram ID пользователя", unique=True)
    user_name = models.CharField(
        max_length=100, verbose_name="Telegram имя пользователя ", blank=True, null=True
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Подразделение')
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Должность')
    full_name = models.CharField(
        max_length=100, verbose_name="ФИО", blank=True, null=True
    )
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", blank=True, null=True)
    first_name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    middle_name = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    date_of_birth = models.CharField(
        max_length=10, verbose_name="Дата рождения", blank=True, null=True
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон", blank=True, null=True
    )
    email = models.CharField(
        max_length=30, verbose_name="Email", blank=True, null=True)
    country = models.CharField(
        max_length=30, verbose_name="Страна", blank=True, null=True)
    # job_title = models.ForeignKey('lightning.JobTitle', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Должность')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('Компания'), null=True, blank=True)
    # department = models.ForeignKey('lightning.Department', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Подразделение')
    language = models.CharField(
        max_length=20, verbose_name="Язык", blank=True, null=True
    )
    tg_mention = models.CharField(
        max_length=100, verbose_name="tg_mention", blank=True, null=True
    )
    image_telegramuser = models.ImageField(
        upload_to="telegramuser",
        null=True,
        blank=True,
        verbose_name="Фото пользователя",
    )    
    testing_process = models.BooleanField(default=False, verbose_name="testing_process")
    current_question_index = models.PositiveSmallIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.full_name:  # Проверяем, что full_name не пустое и не None
            self.last_name, self.first_name, self.middle_name = self.parse_full_name(self.full_name)
        
        # Форматируем телефон и дату рождения перед сохранением
        if self.phone:
            try:
                formatted_phone = self.format_phone(self.phone)
                if formatted_phone:
                    self.phone = formatted_phone
                else:
                    self.phone = None
            except Exception as e:
                self.phone = None  # Устанавливаем в None при ошибке
        
        if self.date_of_birth:
            try:
                formatted_dob = self.format_date_of_birth(self.date_of_birth)
                if formatted_dob:
                    self.date_of_birth = formatted_dob
                else:
                    self.date_of_birth = None
            except Exception as e:
                self.date_of_birth = None  # Устанавливаем в None при ошибке
        
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

    @staticmethod
    def format_phone(phone_str):
        """
        Преобразует номер телефона из формата +71112223344 в +7(111)222-33-44.
        Если формат некорректен, дополняет или обрезает данные.
        Возвращает отформатированный номер или None, если форматирование невозможно.
        """
        # Удаляем все символы, кроме цифр и плюса
        phone_clean = re.sub(r'[^\d+]', '', phone_str)
        
        # Удаляем '+' для подсчета цифр
        phone_digits = re.sub(r'[^\d]', '', phone_clean)
        
        # Проверяем, начинается ли номер с 7 или 8, заменяем на 7
        if phone_digits.startswith('8'):
            phone_digits = '7' + phone_digits[1:]
        elif not phone_digits.startswith('7'):
            phone_digits = '7' + phone_digits
        
        # Дополняем нулями или обрезаем до 11 цифр (7 + 10 цифр)
        if len(phone_digits) < 11:
            phone_digits = phone_digits.ljust(11, '0')
        elif len(phone_digits) > 11:
            phone_digits = phone_digits[:11]
        
        # Форматируем в нужный вид
        formatted_phone = f"+7({phone_digits[1:4]}){phone_digits[4:7]}-{phone_digits[7:9]}-{phone_digits[9:11]}"
        return formatted_phone

    @staticmethod
    def format_date_of_birth(dob_str):
        """
        Преобразует дату рождения из формата '01011990' или '01.01.1990' в '01.01.1990'.
        Если формат некорректен, дополняет недостающие части нулями или обрезает лишние.
        Возвращает отформатированную дату или None, если форматирование невозможно.
        """
        # Удаляем все символы, кроме цифр
        dob_clean = re.sub(r'[^\d]', '', dob_str)
        
        # Дополняем нулями или обрезаем до 8 цифр (ДДММГГГГ)
        if len(dob_clean) < 8:
            dob_clean = dob_clean.ljust(8, '0')
        elif len(dob_clean) > 8:
            dob_clean = dob_clean[:8]
        
        day = dob_clean[0:2]
        month = dob_clean[2:4]
        year = dob_clean[4:8]
        
        # Форматируем дату
        formatted_dob = f"{day}.{month}.{year}"
        return formatted_dob

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        ordering = ["id"]

    def __str__(self):
        # return f'{self.full_name} | {self.user_name}'
        return f'{self.full_name}'


class TelegramGroup(ChangeLoggableMixin, models.Model):
    # lightning_group = models.BooleanField(default=False, verbose_name='Группа для молний')
    name = models.CharField(max_length=100, verbose_name="Наименование группы")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    users = models.ManyToManyField(TelegramUser, blank=True, verbose_name="Пользователи", related_name="groups")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Группа студентов"
        verbose_name_plural = "Группы студентов"
        ordering = ["name"]


class UserRead(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, verbose_name=_('Курс'))
    topic = models.ForeignKey(CourseTopic, on_delete=models.CASCADE, verbose_name=_('Тема курса'))
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course', 'topic')


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
        ordering = ["-timestamp"]


def log_active(model_list):
    for m in model_list:
        post_save.connect(journal_save_handler, sender=m)
        post_delete.connect(journal_delete_handler, sender=m)


log_active([TelegramUser, TelegramGroup])
