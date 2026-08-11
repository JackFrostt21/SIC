from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import JobTitle, Department, Company


class JobTitleResource(resources.ModelResource):
    """
    Ресурс для импорта/экспорта должностей
    """

    class Meta:
        model = JobTitle
        fields = ("id", "name", "source_id", "is_actual")
        export_order = ("id", "name", "source_id", "is_actual")
        import_id_fields = ("id",)
        skip_unchanged = True
        report_skipped = False

    def before_import_row(self, row, **kwargs):
        """
        Обработка строки перед импортом
        """
        # Убираем лишние пробелы из названия должности
        if "name" in row:
            row["name"] = str(row["name"]).strip()

    def before_save_instance(self, instance, using_transactions, dry_run):
        """
        Обработка экземпляра перед сохранением
        """
        # Дополнительная валидация перед сохранением
        if not instance.name:
            raise ValueError("Название должности не может быть пустым")


class DepartmentResource(resources.ModelResource):
    """
    Ресурс для импорта/экспорта подразделений
    """

    company = fields.Field(
        column_name="company",
        attribute="company",
        widget=ForeignKeyWidget(Company, "name"),
    )

    parent = fields.Field(
        column_name="parent",
        attribute="parent",
        widget=ForeignKeyWidget(Department, "name"),
    )

    class Meta:
        model = Department
        fields = (
            "id",
            "name",
            "company",
            "parent",
            "source_id",
            "is_actual",
        )
        export_order = (
            "id",
            "name",
            "company",
            "parent",
            "source_id",
            "is_actual",
        )
        import_id_fields = ("id",)
        skip_unchanged = True
        report_skipped = False

    def before_import_row(self, row, **kwargs):
        """
        Обработка строки перед импортом
        """
        # Убираем лишние пробелы
        if "name" in row:
            row["name"] = str(row["name"]).strip()

    def before_save_instance(self, instance, using_transactions, dry_run):
        """
        Обработка экземпляра перед сохранением
        """
        if not instance.name:
            raise ValueError("Название подразделения не может быть пустым")
        if not instance.company:
            raise ValueError("Подразделение должно принадлежать компании")


class CompanyResource(resources.ModelResource):
    """
    Ресурс для импорта/экспорта компаний
    """

    class Meta:
        model = Company
        fields = ("id", "name", "is_actual")
        export_order = ("id", "name", "is_actual")
        import_id_fields = ("id",)
        skip_unchanged = True
        report_skipped = False

    def before_import_row(self, row, **kwargs):
        """
        Обработка строки перед импортом
        """
        if "name" in row:
            row["name"] = str(row["name"]).strip()

    def before_save_instance(self, instance, using_transactions, dry_run):
        """
        Обработка экземпляра перед сохранением
        """
        if not instance.name:
            raise ValueError("Название компании не может быть пустым")
