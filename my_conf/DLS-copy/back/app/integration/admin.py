from django.contrib import admin
from .models import RegistrationSetting, APISettings


@admin.register(RegistrationSetting)
class RegistrationSettingAdmin(admin.ModelAdmin):
    list_display = ('name', )
    fieldsets = (
        ('Настройки бота регистрации', {
            'fields': ('name', 'telegram_check_url', 'employee_check_url', 'api_key')
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


@admin.register(APISettings)
class APISettingsAdmin(admin.ModelAdmin):
    list_display = ('api_url', 'api_username', 'api_password', 'company')
    fieldsets = (
        ('Настройки API', {
            'fields': ('api_url', 'api_username', 'api_password', 'company')
        }),
    )