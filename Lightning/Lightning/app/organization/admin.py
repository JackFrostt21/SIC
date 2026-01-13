from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX, XLS, CSV
from django.utils.html import format_html
from app.organization.models import Company, Department, JobTitle
from app.organization.resources import (
    CompanyResource,
    DepartmentResource,
    JobTitleResource,
)


class DepartmentInline(admin.TabularInline):
    model = Department
    fields = ("name", "parent", "job_titles_count")
    readonly_fields = ("job_titles_count",)
    extra = 0
    show_change_link = True
    autocomplete_fields = ("parent",)

    @admin.display(description="Кол-во должностей")
    def job_titles_count(self, obj):
        # На форме создания объекта obj может быть пустым — вернём 0
        if obj and getattr(obj, "pk", None):
            return obj.job_titles.count()
        return 0


@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    resource_class = CompanyResource
    formats = (XLSX, XLS, CSV)

    list_display = ("name", "logo_preview", "departments_count")
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("logo_preview",)
    inlines = (DepartmentInline,)

    @admin.display(description="Логотип")
    def logo_preview(self, obj):
        if obj.logo:
            try:
                return format_html(
                    '<img src="{}" style="max-height:40px;"/>', obj.logo.url
                )
            except Exception:
                return "—"
        return "—"

    @admin.display(description="Кол-во отделов")
    def departments_count(self, obj):
        return obj.departments.count()


@admin.register(JobTitle)
class JobTitleAdmin(ImportExportModelAdmin):
    resource_class = JobTitleResource
    formats = (XLSX, XLS, CSV)

    list_display = ("id","name", "departments_count")
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("source_id", "id")

    @admin.display(description="Где используется (отделов)")
    def departments_count(self, obj):
        return obj.departments_of_job_title.count()


@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    formats = (XLSX, XLS, CSV)

    list_display = ("id", "name", "company", "parent", "job_titles_count", "children_count")
    list_filter = ("company",)
    search_fields = ("name", "company__name", "parent__name", "job_titles__name")
    ordering = ("company__name", "name")

    filter_horizontal = ("job_titles",)
    autocomplete_fields = ("company", "parent")
    raw_id_fields = ()
    readonly_fields = ("source_id", "id")

    fieldsets = (
        ("Принадлежность", {"fields": ("source_id", "company", "parent")}),
        ("Основное", {"fields": ("name", "job_titles")}),
    )

    @admin.display(description="Кол-во должностей")
    def job_titles_count(self, obj):
        return obj.job_titles.count()

    @admin.display(description="Кол-во подчинённых")
    def children_count(self, obj):
        return obj.children.count()