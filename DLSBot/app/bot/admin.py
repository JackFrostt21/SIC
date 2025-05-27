from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser, TelegramGroup, UserRead, UserTest


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name', 'user_name', 'phone', 'email', 'state', 'is_actual')
    list_filter = ('is_actual', 'state', 'company', 'department', 'job_title')
    search_fields = ('user_id', 'full_name', 'user_name', 'phone', 'email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('user_id', 'user_name', 'full_name', 'image', 'created_at', 'updated_at')
        }),
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name', 'date_of_birth', 'phone', 'email')
        }),
        ('Организация', {
            'fields': ('company', 'department', 'job_title')
        }),
        ('Настройки и состояние', {
            'fields': ('language', 'is_actual', 'state')
        }),
    )


@admin.register(TelegramGroup)
class TelegramGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'user_count', 'is_actual')
    list_filter = ('is_actual',)
    search_fields = ('name', 'description')
    filter_horizontal = ('users',)
    readonly_fields = ('created_at', 'updated_at')
    
    def description_short(self, obj):
        if obj.description and len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description or "-"
    
    description_short.short_description = "Описание"
    
    def user_count(self, obj):
        return obj.users.count()
    
    user_count.short_description = "Кол-во пользователей"


@admin.register(UserRead)
class UserReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'topic', 'is_read', 'read_at')
    list_filter = ('is_read', 'read_at', 'course', 'topic')
    search_fields = ('user__full_name', 'user__user_name', 'course__title', 'topic__title')
    date_hierarchy = 'read_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserTest)
class UserTestAdmin(admin.ModelAdmin):
    list_display = ('user', 'training', 'complete', 'results_display', 'created_at')
    list_filter = ('complete', 'training')
    search_fields = ('user__full_name', 'user__user_name', 'training__title')
    readonly_fields = ('user_answer', 'created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'training', 'question', 'is_actual', 'created_at', 'updated_at')
        }),
        ('Результаты', {
            'fields': ('complete', 'quantity_correct', 'quantity_not_correct')
        }),
        ('Ответы пользователя', {
            'classes': ('collapse',), # скрывает поле ответы пользователя
            'fields': ('user_answer',) # показывает поле ответы пользователя
        }),
    )
    
    def results_display(self, obj):
        if obj.quantity_correct is not None:
            return format_html(
                '<span style="color: {};">{} / {}</span>',
                'green' if obj.complete else 'red',
                obj.quantity_correct or 0,
                100
            )
        return "-"
    
    results_display.short_description = "Результаты"
