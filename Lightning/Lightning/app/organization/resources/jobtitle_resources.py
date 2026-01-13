from import_export import resources, fields
from app.organization.models import JobTitle


class JobTitleResource(resources.ModelResource):
    id = fields.Field(column_name='ID', attribute='id', readonly=False)
    name = fields.Field(column_name='Название должности', attribute='name')

    class Meta:
        model = JobTitle
        fields = ('id', 'name')
        export_order = ('id', 'name')
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
            raise ValueError("Поле Название должности не может быть пустым")