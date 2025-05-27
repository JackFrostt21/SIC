from django.db import models
from django_ckeditor_5.fields import CKEditor5Field 

from app.core.abstract_models import BaseModel
from .courses import TrainingCourse


class Certificate(BaseModel):
    """
    Сертификат о прохождении курса
    """
    user = models.ForeignKey(
        "bot.TelegramUser", 
        on_delete=models.CASCADE, 
        related_name='certificates', 
        verbose_name='Студент'
    )
    training_course = models.ForeignKey(
        TrainingCourse, 
        on_delete=models.CASCADE, 
        related_name='certificates', 
        verbose_name='Программа обучения'
    )
    result = models.IntegerField(verbose_name='Результат')
    certificate_file = models.FileField(
        upload_to='certificates/', 
        verbose_name='Адрес файла', 
        blank=True
    )

    def __str__(self):
        return f"{self.user} - {self.training_course} - {self.result}%"

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'


class RatingTrainingCourse(BaseModel):
    """
    Рейтинг программы обучения
    """
    training_course = models.ForeignKey(
        TrainingCourse, 
        on_delete=models.CASCADE, 
        verbose_name='Программа обучения', 
        related_name='rating_course'
    )
    student = models.ForeignKey(
        'bot.TelegramUser', 
        on_delete=models.CASCADE, 
        verbose_name='Студент'
    )
    rating = models.IntegerField(verbose_name='Оценка')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    def __str__(self):
        return f"{self.student} - {self.training_course} - {self.rating}"

    class Meta:
        verbose_name = 'Рейтинг программы'
        verbose_name_plural = 'Рейтинги программ'


class CourseDeadline(BaseModel):
    """
    Дедлайн для программы обучения
    """
    deadline_date = models.DateField(verbose_name='Дата дедлайна')
    training_course = models.ForeignKey(
        TrainingCourse, 
        on_delete=models.CASCADE, 
        related_name='deadlines', 
        verbose_name='Программа обучения'
    )
    deadline_groups = models.ManyToManyField(
        "bot.TelegramGroup", 
        blank=True, 
        related_name='deadlines', 
        verbose_name='Группы'
    )
    deadline_users = models.ManyToManyField(
        "bot.TelegramUser", 
        blank=True, 
        related_name='deadlines', 
        verbose_name='Студенты'
    )

    class Meta:
        verbose_name = 'Дедлайн'
        verbose_name_plural = 'Дедлайны'

    def __str__(self):
        return f"{self.training_course} - {self.deadline_date}"


class NewsBlock(BaseModel):
    """
    Новостной блок
    """
    news_title = models.CharField(max_length=100, verbose_name='Наименование', default='Новости')
    start_date_news = models.DateField(verbose_name='Дата старта новости')
    end_date_news = models.DateField(null=True, blank=True, verbose_name='Дата завершения новости')
    text_news = CKEditor5Field(config_name='default', null=True, blank=True, verbose_name='Текст новости')
    image = models.ImageField(
        upload_to="news", 
        null=True, 
        blank=True, 
        verbose_name="Изображение новости"
    )
    is_published = models.BooleanField(
        default=True, 
        verbose_name='Опубликовано'
    )

    def __str__(self):
        return self.news_title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-start_date_news"]