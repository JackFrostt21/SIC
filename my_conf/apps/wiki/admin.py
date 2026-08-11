from django.contrib import admin
from .models import Project, Page


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
