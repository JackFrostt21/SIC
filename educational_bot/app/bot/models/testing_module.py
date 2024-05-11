from django.db import models
from django.utils.translation import gettext as _

from app.core.abstract_models import BaseModel, BaseRowStateModel

from django.db.models.signals import post_save, post_delete
from app.core.mixins import ChangeLoggableMixin
from app.core.signals import journal_save_handler, journal_delete_handler

def default_user_answer():
    return {"results": []}

class UserTest(BaseModel, BaseRowStateModel, ChangeLoggableMixin):
    question = models.ForeignKey("educational_module.TopicQuestion", on_delete=models.DO_NOTHING, null=True, blank=True,
                                 verbose_name=_("question"))
    user = models.ForeignKey("bot.TelegramUser", on_delete=models.DO_NOTHING, null=True, blank=True,
                             verbose_name=_("user"))
    training = models.ForeignKey("educational_module.TrainingCourse", on_delete=models.DO_NOTHING, null=True,
                                 blank=True,
                                 verbose_name=_("training"))

    user_answer = models.JSONField(verbose_name=_("user answer"), default=default_user_answer)
    complete = models.BooleanField(default=False, verbose_name=_("complete"))

    quantity_correct = models.PositiveSmallIntegerField(null=True, blank=True)
    quantity_not_correct = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _("UserTest")
        verbose_name_plural = _("UserTests")

    def __str__(self):
        return f"{self.question} | {self.user} | {self.complete} |"
    
def log_active(model_list):
    for m in model_list:
        post_save.connect(journal_save_handler, sender=m)
        post_delete.connect(journal_delete_handler, sender=m)


log_active([UserTest])
