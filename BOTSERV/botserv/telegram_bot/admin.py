from django.contrib import admin
from .models import TelegramUser, DirectoryServices, ApplicationForm, Applications

admin.site.register(TelegramUser)
admin.site.register(DirectoryServices)
# admin.site.register(ApplicationForm)
admin.site.register(Applications)