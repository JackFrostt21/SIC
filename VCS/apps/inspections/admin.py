from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline

from apps.inspections.models import Inspection, InspectionFile


class InspectionFileInline(TabularInline):
    model = InspectionFile
    extra = 0
    autocomplete_fields = ("uploaded_by",)
    fields = (
        "file_name",
        "file_url",
        "mime_type",
        "size_bytes",
        "uploaded_by",
        "uploaded_at",
    )
    readonly_fields = ("uploaded_at",)


@admin.register(Inspection)
class InspectionAdmin(ModelAdmin):
    list_display = (
        "inspection_date",
        "vehicle",
        "created_by",
        "created_at",
        "deleted_at",
    )
    list_filter = ("inspection_date", "deleted_at")
    search_fields = ("vehicle__plate_number", "created_by__username")
    autocomplete_fields = ("vehicle", "created_by")
    inlines = (InspectionFileInline,)
    ordering = ("-inspection_date", "-created_at")

    def save_model(self, request, obj, form, change):
        if obj.created_by_id is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(InspectionFile)
class InspectionFileAdmin(ModelAdmin):
    list_display = (
        "file_name",
        "inspection",
        "mime_type",
        "uploaded_at",
    )
    search_fields = ("file_name", "inspection__vehicle__plate_number")
    autocomplete_fields = ("inspection", "uploaded_by")
    ordering = ("-uploaded_at", "file_name")
