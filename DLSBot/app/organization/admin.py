from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import JobTitle, Department, Company, SettingsBot


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_actual')
    list_filter = ('is_actual',)
    search_fields = ('name', 'source_id')
    readonly_fields = ('created_at', 'updated_at')


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1
    fields = ('name', 'source_id', 'parent', 'is_actual') 
    fk_name = 'company'
    verbose_name = "Подразделение"
    verbose_name_plural = "Подразделения"

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'job_titles_count', 'is_actual')
    list_filter = ('is_actual', 'parent')
    search_fields = ('name', 'source_id')
    filter_horizontal = ('job_titles',)
    readonly_fields = ('created_at', 'updated_at')
    
    def job_titles_count(self, obj):
        return obj.job_titles.count()
    
    job_titles_count.short_description = "Должностей"


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_logo', 'is_actual')
    list_filter = ('is_actual',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'display_logo')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'is_actual', 'created_at', 'updated_at')
        }),
        ('Фирменный стиль', {
            'fields': ('logo', 'display_logo', 'certificate_template')
        }),
    )
    inlines = [DepartmentInline]
    
    def display_logo(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" width="100" />')
        return "Нет логотипа"
    
    display_logo.short_description = "Логотип"


@admin.register(SettingsBot)
class SettingsBotAdmin(admin.ModelAdmin):
    list_display = ('company', 'bot_version', 'is_actual')
    list_filter = ('is_actual', 'company')
    search_fields = ('company__name', 'bot_version')
    readonly_fields = (
        'created_at', 'updated_at',
        'preview_image_start', 'preview_image_list_courses', 'preview_image_settings',
        'preview_image_progress', 'preview_image_test_passed', 'preview_image_test_failed',
        'preview_image_test_start', 'preview_image_help', 'preview_image_progress_good',
        'preview_image_progress_bad'
    )
    fieldsets = (
        ('Основная информация', {
            'fields': ('is_actual', 'company', 'url_web_app', 'created_at', 'updated_at')
        }),
        ('Справочная информация', {
            'fields': ('bot_help_text', 'bot_version')
        }),
        ('Изображения для бота', {
            'classes': ('collapse',),
            'fields': (
                'image_start', 'preview_image_start',
                'image_list_courses', 'preview_image_list_courses',
                'image_settings', 'preview_image_settings',
                'image_progress', 'preview_image_progress'
            )
        }),
        ('Изображения для тестирования', {
            'classes': ('collapse',),
            'fields': (
                'image_test_passed', 'preview_image_test_passed',
                'image_test_failed', 'preview_image_test_failed',
                'image_test_start', 'preview_image_test_start'
            )
        }),
        ('Изображения для прогресса', {
            'classes': ('collapse',),
            'fields': (
                'image_progress_good', 'preview_image_progress_good',
                'image_progress_bad', 'preview_image_progress_bad'
            )
        }),
        ('Изображения для справки', {
            'classes': ('collapse',),
            'fields': ('image_help', 'preview_image_help')
        }),
    )
    
    def preview_image_start(self, obj):
        return self._preview_image(obj.image_start)
    
    def preview_image_list_courses(self, obj):
        return self._preview_image(obj.image_list_courses)
    
    def preview_image_settings(self, obj):
        return self._preview_image(obj.image_settings)
    
    def preview_image_progress(self, obj):
        return self._preview_image(obj.image_progress)
    
    def preview_image_test_passed(self, obj):
        return self._preview_image(obj.image_test_passed)
    
    def preview_image_test_failed(self, obj):
        return self._preview_image(obj.image_test_failed)
    
    def preview_image_test_start(self, obj):
        return self._preview_image(obj.image_test_start)
    
    def preview_image_help(self, obj):
        return self._preview_image(obj.image_help)
    
    def preview_image_progress_good(self, obj):
        return self._preview_image(obj.image_progress_good)
    
    def preview_image_progress_bad(self, obj):
        return self._preview_image(obj.image_progress_bad)
    
    def _preview_image(self, image_field):
        if image_field:
            return mark_safe(f'<img src="{image_field.url}" width="150" />')
        return "Нет изображения"
    
    preview_image_start.short_description = "Предпросмотр"
    preview_image_list_courses.short_description = "Предпросмотр"
    preview_image_settings.short_description = "Предпросмотр"
    preview_image_progress.short_description = "Предпросмотр"
    preview_image_test_passed.short_description = "Предпросмотр"
    preview_image_test_failed.short_description = "Предпросмотр"
    preview_image_test_start.short_description = "Предпросмотр"
    preview_image_help.short_description = "Предпросмотр"
    preview_image_progress_good.short_description = "Предпросмотр"
    preview_image_progress_bad.short_description = "Предпросмотр"