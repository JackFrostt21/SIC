from django.db import models


class BaseModel(models.Model):
    """
    id: Автоматически генерируемое поле, служащее первичным ключом. Использует BigAutoField для поддержки большого количества записей.
    created_at: Дата и время создания записи, автоматически устанавливается при создании объекта.
    updated_at: Дата и время последнего обновления записи, автоматически обновляется каждый раз при сохранении объекта.
    is_actual: Булево поле, указывающее актуальность записи, по умолчанию False.
    """
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True,
                             verbose_name='internal_id')
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, verbose_name='created_at')
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True, verbose_name='updated_at')
    is_actual = models.BooleanField(verbose_name='Отобразить', default=False)

    class Meta:
        abstract = True


class BaseRowStateModel(models.Model): # Для моделей с состояниями
    STATE_NOT_ACTIVE = 0
    STATE_ACTIVE = 1
    STATE_DELETED = 2
    # Список состояний
    REF_STATES = ((STATE_NOT_ACTIVE, 'NOT_ACTIVE'), (STATE_ACTIVE, 'ACTIVE'), (STATE_DELETED, 'DELETED'))
    state = models.IntegerField(choices=REF_STATES, default=STATE_NOT_ACTIVE, null=True, verbose_name='state')

    class Meta:
        abstract = True
