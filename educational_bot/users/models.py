from django.db import models
from django.contrib.auth.models import AbstractUser

from django.db.models.signals import post_save, post_delete
from app.core.mixins import ChangeLoggableMixin
from app.core.signals import journal_save_handler, journal_delete_handler

class CustomUser(AbstractUser, ChangeLoggableMixin):
    pass

def log_active(model_list):
    for m in model_list:
        post_save.connect(journal_save_handler, sender=m)
        post_delete.connect(journal_delete_handler, sender=m)


log_active([CustomUser])