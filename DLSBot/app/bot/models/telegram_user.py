from django.db import models
import re

from app.core.abstract_models import BaseModel, BaseRowStateModel
from app.organization.models import Company, Department, JobTitle



#TODO: Добавить в модели индексы

class TelegramUser(BaseModel, BaseRowStateModel):
    """
    Модель пользователя Telegram
    """
    user_id = models.BigIntegerField(verbose_name="Telegram ID", unique=True)
    user_name = models.CharField(max_length=100, verbose_name="Username", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Компания', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Подразделение')
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Должность')
    full_name = models.CharField(max_length=100, verbose_name="ФИО", blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", blank=True, null=True)
    first_name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    middle_name = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    date_of_birth = models.CharField(max_length=10, verbose_name="Дата рождения", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True, null=True)
    email = models.EmailField(max_length=50, verbose_name="Email", blank=True, null=True)
    language = models.CharField(max_length=20, verbose_name="Язык", blank=True, null=True, default='ru')
    image = models.ImageField(upload_to="telegramuser", null=True, blank=True, verbose_name="Фото пользователя")


    def save(self, *args, **kwargs):
        if self.full_name:
            self.last_name, self.first_name, self.middle_name = self.parse_full_name(self.full_name)
        
        # Форматирование телефона
        if self.phone:
            try:
                formatted_phone = self.format_phone(self.phone)
                if formatted_phone:
                    self.phone = formatted_phone
                else:
                    self.phone = None
            except Exception:
                self.phone = None
        
        # Форматирование даты рождения
        if self.date_of_birth:
            try:
                formatted_dob = self.format_date_of_birth(self.date_of_birth)
                if formatted_dob:
                    self.date_of_birth = formatted_dob
                else:
                    self.date_of_birth = None
            except Exception:
                self.date_of_birth = None
        
        super().save(*args, **kwargs)

    @staticmethod
    def parse_full_name(full_name):
        """Разбивает полное имя на фамилию, имя и отчество"""
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
        Преобразует номер телефона в формат +7(XXX)XXX-XX-XX
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
        Преобразует дату рождения в формат DD.MM.YYYY
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
        return f'{self.full_name or self.user_name or f"ID: {self.user_id}"}'


class TelegramGroup(BaseModel):
    """
    Модель группы пользователей Telegram
    """
    name = models.CharField(max_length=100, verbose_name="Наименование группы")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    users = models.ManyToManyField(
        TelegramUser, 
        blank=True, 
        verbose_name="Пользователи", 
        related_name="groups"
    )

    class Meta:
        verbose_name = "Группа студентов"
        verbose_name_plural = "Группы студентов"
        ordering = ["name"]

    def __str__(self):
        return self.name