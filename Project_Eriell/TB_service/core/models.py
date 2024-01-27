from django.db import models

class TelegramUser(models.Model):
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

    class Meta:
        verbose_name = 'TelegramUser'
        
        #определяем отображение множественного наименования
        verbose_name_plural = "TelegramUser's" 
        
        #определяем порядок сортировки объектов модели по id
        ordering = ['id'] #

    def __str__(self):

        if self.user_name is None or self.phone is None:
            logo = f'{self.tg_mention} | {self.user_id}'
        else:
            logo = f' {self.user_name} | Tel: {self.phone} '

        return logo
