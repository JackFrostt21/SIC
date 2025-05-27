from django.db import models
from django.utils.translation import gettext_lazy as _


""" 
Добавить индексацию для полей (is_actual, state)
"""

class BaseModel(models.Model):
    """
    Базовая модель с полями id, created_at, updated_at, is_actual
    - id: Автоматически генерируемое поле, первичный ключ
    - created_at: Дата и время создания записи
    - updated_at: Дата и время последнего обновления записи
    - is_actual: Флаг актуальности записи
    """
    # TODO: подумать, нужно ли это поле is_actual везде

    id = models.BigAutoField(
        auto_created=True, primary_key=True, serialize=True, verbose_name=_("ID")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, null=True, verbose_name=_("Created at")
    )
    updated_at = models.DateTimeField(
        auto_now=True, editable=False, null=True, verbose_name=_("Updated at")
    )
    is_actual = models.BooleanField(verbose_name=_("Is actual"), default=True)

    class Meta:
        abstract = True


class BaseRowStateModel(models.Model):
    """
    Модель с состояниями записи (неактивна, активна, удалена)
    """

    STATE_NOT_ACTIVE = 0
    STATE_ACTIVE = 1
    STATE_DELETED = 2

    REF_STATES = (
        (STATE_NOT_ACTIVE, _("Not active")),
        (STATE_ACTIVE, _("Active")),
        (STATE_DELETED, _("Deleted")),
    )

    state = models.IntegerField(
        choices=REF_STATES, default=STATE_NOT_ACTIVE, null=True, verbose_name=_("State")
    )

    class Meta:
        abstract = True
