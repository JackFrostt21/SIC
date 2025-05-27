from django.contrib import admin
from .models import JobTitle, Department


@admin.register(JobTitle)
class JobTitleModeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Department)
class DepartmentModeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)