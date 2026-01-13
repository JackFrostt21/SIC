from django.db import models


class RowStateModel(models.Model):  # Для моделей с состояниями
    STATE_NOT_ACTIVE = 0
    STATE_ACTIVE = 1
    STATE_DELETED = 2
    STATE_NEED_CONFIRMATION = 3
    
    # Список состояний
    REF_STATES = (
        (STATE_NOT_ACTIVE, 'Неактивный'),
        (STATE_ACTIVE, 'Активный'),
        (STATE_DELETED, 'Удалённый'),
        (STATE_NEED_CONFIRMATION, 'Нужно подтвердить'),
    )

    state = models.IntegerField(
        choices=REF_STATES,
        default=STATE_NOT_ACTIVE,
        null=True,
        verbose_name='Статус'
    )

    class Meta:
        abstract = True