from django.contrib import admin
from .models import RegistrationSetting


@admin.register(RegistrationSetting)
class RegistrationSettingAdmin(admin.ModelAdmin):
    list_display = ('regbot_active', 'regbot_api_url', 'regbot_telegram_url')
    fieldsets = (
        ('Настройки бота регистрации', {
            'fields': ('regbot_active', 'regbot_api_url', 'regbot_telegram_url', 'api_key')
        }),
        ('Настройки приветствия', {
            'fields': ('send_welcome_message', 'welcome_message_text')
        }),
    )
    
    def has_add_permission(self, request):
        # Ограничиваем создание только одной записи с настройками
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
        
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление единственной записи
        return False
