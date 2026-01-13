from django.contrib import admin

from app.scheduler.models.log_models import SchedulerLog


@admin.register(SchedulerLog)
class SchedulerLogAdmin(admin.ModelAdmin):
    list_display = ("task_name", "status", "start_time", "end_time", "execution_time")
    list_filter = ("status", "start_time", "end_time")
    search_fields = ("task_name", "status", "start_time", "end_time", "execution_time")
    readonly_fields = ("task_name", "status", "start_time", "end_time", "execution_time")
    date_hierarchy = "start_time"
    ordering = ("-start_time",)
    list_per_page = 100
    list_max_show_all = 1000
    list_editable = ("status",)