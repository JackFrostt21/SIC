# from django.contrib import admin
# from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserCreationForm, CustomUserChangeForm
# from .models import CustomUser

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ['email', 'username',]

# admin.site.register(CustomUser, CustomUserAdmin)

from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_superuser')
#     list_display_links = ('email',)
#     search_fields = ('user_id', 'user_name', 'created_at', 'updated_at')


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_display_links = None
    list_filter = ('action_time', 'action_flag')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        ##если суперпольз то отдаем все записи
        if request.user.is_superuser:
            return qs
        ##если НЕ суперпольз то отдаем только записи активного пользователя
        return qs.filter(user=request.user)
    

    ###РАЗОБРАТЬСЯ при добавлении пропадает кликабельность на админ панели
    def has_add_permission(self, request):
        # Запрет на добавление новых записей
        return False

    def has_delete_permission(self, request, obj=None):
        # Запрет на удаление записей
        return False

    def has_change_permission(self, request, obj=None):
        # Запрет на изменение записей
        return False