from django.db import models
from django.conf import settings
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from app.core.abstract_models import BaseModel
from django.utils.translation import get_language
from django.contrib.auth.models import AbstractUser


ACTION_CREATE = 'create'
ACTION_UPDATE = 'update'
ACTION_DELETE = 'delete'


# на сайте как "Модели" Нужно заменить на Журнал событий или как то так
class ChangeLog(models.Model):
    #Перечень что логируем
    TYPE_ACTION_ON_MODEL = (
        (ACTION_CREATE, _('ACTION_CREATE')),
        (ACTION_UPDATE, _('ACTION_UPDATE')),
        (ACTION_DELETE, _('ACTION_DELETE')),
    )

    """
    changed: Дата и время изменения.
    model: Название модели, в которой произошло изменение.
    record_id: Идентификатор записи, которая была изменена.
    user: Связь с пользователем, который совершил изменение.
    action_on_model: Тип действия, принятого к модели.
    data_history: Поле JSON для хранения истории данных до изменения.
    data: Поле JSON для хранения текущих данных после изменения.
    ipaddress: IP-адрес пользователя, совершившего изменение.
    """
    changed = models.DateTimeField(auto_now=True, verbose_name=_('changed'))
    model = models.CharField(max_length=255, verbose_name=_('model'), null=True)
    record_id = models.IntegerField(verbose_name=_('record_id'), null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('user'),
        on_delete=models.CASCADE, null=True)
    action_on_model = models.CharField(
        choices=TYPE_ACTION_ON_MODEL, max_length=50, verbose_name=_('action'), null=True)
    data_history = JSONField(verbose_name=_('data_history'), default=dict)
    data = JSONField(verbose_name=_('data'), default=dict)

    ipaddress = models.CharField(max_length=15, verbose_name=_('ipaddress'), null=True)

    class Meta:
        ordering = ('-changed',) #поменял по убыванию
        verbose_name = _('Change log')
        verbose_name_plural = _('Changes log')

    @classmethod
    def add(cls, instance, user, ipaddress, action_on_model, data_history, data, id=None):
        log = ChangeLog.objects.get(id=id) if id else ChangeLog() #нашли, обновляем, нет создаем новый
        log.model = instance.__class__.__name__
        log.record_id = instance.pk
        if user:
            log.user = user
        log.ipaddress = ipaddress
        log.action_on_model = action_on_model
        log.data = data_history # НЕТ ДАННЫХ!!!
        log.data = data
        log.save()
        return log.pk


# в админке как Логи запросов
class RequestLog(BaseModel):
    class LogType(models.TextChoices):
        OUTPUT = ('OUTPUT', 'Output')
        INPUT = ('INPUT', 'Input')

    url = models.CharField(max_length=600, null=True, blank=True)
    text = models.TextField(null=True)
    response = models.TextField(null=True)
    log_type = models.CharField(choices=LogType.choices, max_length=50)

    @classmethod
    def add(cls, url, text, response, log_type, id=None):
        log = RequestLog.objects.get(id=id) if id else RequestLog()
        log.url = url
        log.text = text
        log.response = response
        log.log_type = log_type
        log.save()
        return log.id

    class Meta:
        verbose_name = "Request Log"
        verbose_name_plural = "Requests Log"
        ordering = ['-id']

    def __str__(self):
        return f'{self.url}'

# в админке как Логи Обмена
class ExchangeLog(models.Model):
    exchange_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, verbose_name='exchange_date')

    class Meta:
        verbose_name = 'ExchangeLog'
        verbose_name_plural = 'ExchangeLogs'
        ordering = ['-id']

#На стартовую панель не выведена (указано как - динамическую модель для обмена)
class DynamicModel(models.Model):
    """
    Dynamic Model for Exchange
    """
    internal_id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True,
                                      verbose_name='internal_id')
    instance = models.IntegerField(blank=True, null=True, verbose_name='instance')  # id instance
    exchange_date = models.DateTimeField(auto_now_add=True, editable=False, null=True, verbose_name='exchange_date')
    id = models.PositiveBigIntegerField(blank=True, null=True, verbose_name='external_id')

    model = models.CharField(max_length=100, blank=True, null=True)
    dynamic_data = models.JSONField()
    exchange_log = models.ForeignKey(ExchangeLog, verbose_name=_('exchange_log'), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'DynamicModel'
        verbose_name_plural = 'DynamicModels'
        ordering = ['-exchange_date']

#РАЗОБРАТЬСЯ, в коде более не встречается
class BaseConstModel(models.Model):
    id = models.CharField(auto_created=False, primary_key=True, serialize=True, verbose_name='id', max_length=50)
    title = models.CharField(max_length=500, verbose_name='title', blank=True, null=True)
    ru_title = models.CharField(max_length=500, verbose_name='ru_title', blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        if get_language() == 'ru':
            return f'{self.ru_title}'
        else:
            return f'{self.title}'

    @classmethod
    def get(cls, i):
        try:
            obj = (cls.objects.filter(id=i))
            return obj[0]
        except Exception as e:
            print(e)
            return None