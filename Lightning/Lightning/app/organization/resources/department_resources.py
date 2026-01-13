from import_export import resources, fields
from app.organization.models import Department, Company, JobTitle
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget


class DepartmentResource(resources.ModelResource):
    id = fields.Field(column_name='ID', attribute='id', readonly=False)
    company = fields.Field(
        column_name='Компания',
        attribute='company',
        widget=ForeignKeyWidget(Company, 'name')
    )
    parent = fields.Field(
        column_name='Родительский отдел',
        attribute='parent',
        widget=ForeignKeyWidget(Department, 'id')
    )
    name = fields.Field(column_name='Название отдела', attribute='name')
    job_titles = fields.Field(
        column_name='Должности (названия через ;)',
        attribute='job_titles',
        widget=ManyToManyWidget(JobTitle, field='name', separator=';')
    )

    class Meta:
        model = Department
        fields = ('id', 'company', 'parent', 'name', 'job_titles')
        export_order = ('id', 'company', 'parent', 'name', 'job_titles')
        import_id_fields = ('id', 'name')
        skip_unchanged = True
        report_skipped = False
        use_transactions = True

    def before_save_instance(self, instance, row, **kwargs):
        """
        Обработка экземпляра перед сохранением
        """
        # Проверяем обязательное поле name
        if not instance.name:
            raise ValueError("Поле Название отдела не может быть пустым")