from django.contrib import admin
from app.core.models import ChangeLog, RequestLog, DynamicModel, ExchangeLog
from django.utils.translation import gettext_lazy as _

admin.site.site_title = _('Admin')
admin.site.site_header = _('Admin')


# Register your models here.

@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ('changed', 'model', 'user', 'record_id', 'data',
                    'ipaddress', 'action_on_model',)
    readonly_fields = ('user',)
    list_filter = ('model', 'action_on_model',)


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'url',)
    list_filter = ('id', 'url',)


@admin.register(DynamicModel)
class DynamicModelAdmin(admin.ModelAdmin):
    list_display = ('internal_id', 'model', 'exchange_date', 'id', 'instance')
    list_display_links = ('internal_id', 'instance', 'model')
    readonly_fields = ('exchange_date',)
    list_filter = ('internal_id', 'instance', 'model', 'exchange_date')


@admin.register(ExchangeLog)
class ExchangeLogAdmin(admin.ModelAdmin):
    list_display = ('exchange_date', 'id')
    list_display_links = ('exchange_date', 'id')
    list_filter = ('exchange_date', 'id')
