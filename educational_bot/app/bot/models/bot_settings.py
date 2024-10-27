from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from django.db.models.signals import post_save, post_delete
from app.core.mixins import ChangeLoggableMixin
from app.core.signals import journal_save_handler, journal_delete_handler

# Create your models here.
class SetsList(ChangeLoggableMixin, models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name=_('id'))
    title = models.CharField(max_length=100, verbose_name=_('title'), blank=True, null=True)
    tag = models.CharField(max_length=50, verbose_name=_('tag'), blank=True, null=True)

    class Meta:
        db_table = "settings"
        verbose_name = _('settings')
        verbose_name_plural = _('settings')
        # proxy = True
        ordering = ['id']

    def __str__(self):
        return f'{self.title}'


class SetsListParameter(ChangeLoggableMixin, models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name=_('id'))
    sets_list = models.ForeignKey(SetsList, verbose_name=_('settings'), blank=True,
                                  on_delete=models.CASCADE, null=True, related_name='SetsListParameter')
    title = models.CharField(max_length=100, verbose_name=_('title'), blank=True, null=True)
    tag = models.CharField(max_length=50, verbose_name=_('tag'), blank=True, null=True)
    value = models.CharField(max_length=200, blank=True, null=False, verbose_name=_('value'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    photo = models.ImageField(upload_to='settings/uploads_photo', verbose_name=_('photo'), blank=True, null=True)

    def photo_preview(self):
        if self.photo:
            return mark_safe('<img src="%s" style="max-width: 400px; max-height: 200px;" />' % self.photo.url)
        else:
            return _('No Image Found')

    photo_preview.short_description = _('photo_preview')

    class Meta:
        verbose_name = _('sets parameter')
        verbose_name_plural = _('sets parameters')
        ordering = ['id']

    def __str__(self):
        return f'{self.title}'
    

def log_active(model_list):
    for m in model_list:
        post_save.connect(journal_save_handler, sender=m)
        post_delete.connect(journal_delete_handler, sender=m)


log_active([SetsList, SetsListParameter])
