from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, BooleanWidget, IntegerWidget
from app.lightning.models import LightningAnswer, LightningQuestion


class LightningAnswerResource(resources.ModelResource):
    id = fields.Field(column_name='ID', attribute='id', readonly=False)
    question = fields.Field(
        column_name='Вопрос (ID)',
        attribute='question',
        widget=ForeignKeyWidget(LightningQuestion, 'id')
    )
    text = fields.Field(
        column_name='Текст ответа',
        attribute='text',
    )
    is_correct = fields.Field(
        column_name='Правильный ответ',
        attribute='is_correct',
        widget=BooleanWidget()
    )
    order = fields.Field(
        column_name='Порядок',
        attribute='order',
        widget=IntegerWidget()
    )

    class Meta:
        model = LightningAnswer
        fields = ('id', 'question', 'text', 'is_correct', 'order')
        export_order = ('id', 'question', 'text', 'is_correct', 'order')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_transactions = True

    def before_save_instance(self, instance, row, **kwargs):
        """
        Обработка экземпляра перед сохранением
        """
            
        if not instance.text:
            raise ValueError("Поле Текст ответа не может быть пустым")