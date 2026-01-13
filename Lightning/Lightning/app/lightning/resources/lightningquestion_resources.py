from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, BooleanWidget, IntegerWidget
from app.lightning.models import LightningQuestion, Lightning


class LightningQuestionResource(resources.ModelResource):
    id = fields.Field(column_name='ID', attribute='id', readonly=False)
    lightning = fields.Field(
        column_name='Молния',
        attribute='lightning',
        widget=ForeignKeyWidget(Lightning, 'id')
    )
    is_multiple_choice = fields.Field(
        column_name='Несколько ответов',
        attribute='is_multiple_choice',
        widget=BooleanWidget()
    )
    order = fields.Field(
        column_name='Порядок',
        attribute='order',
        widget=IntegerWidget()
    )
    name = fields.Field(
        column_name='Вопрос',
        attribute='name',
    )

    class Meta:
        model = LightningQuestion
        fields = ('id', 'lightning', 'name', 'is_multiple_choice', 'order')
        export_order = ('id', 'lightning', 'name', 'is_multiple_choice', 'order')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_transactions = True     

    def before_save_instance(self, instance, row, **kwargs):
        """
        Обработка экземпляра перед сохранением
        """
        #Проверяем обязательное поле id
        if not instance.id:
            raise ValueError("Поле ID не может быть пустым")
        
        if not instance.name:
            raise ValueError("Поле Вопрос не может быть пустым")