from import_export import resources, fields
from app.organization.models import Company


class CompanyResource(resources.ModelResource):
    id = fields.Field(column_name='ID', attribute='id', readonly=False)
    name = fields.Field(column_name='Название компании', attribute='name')
    logo = fields.Field(column_name='Логотип (путь)', attribute='logo')

    class Meta:
        model = Company
        fields = ('id', 'name', 'logo')
        export_order = ('id', 'name', 'logo')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_transactions = True

    def before_save_instance(self, instance, row, **kwargs):
        """
        Обработка экземпляра перед сохранением
        """
        # Проверяем обязательное поле name
        if not instance.name:
            raise ValueError("Поле Название компании не может быть пустым")