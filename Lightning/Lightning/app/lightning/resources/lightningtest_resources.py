from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, BooleanWidget, IntegerWidget
from app.lightning.models import LightningTest, Lightning
from app.bot.models import TelegramUser


class LightningTestResource(resources.ModelResource):
    id = fields.Field(column_name='ID', attribute='id', readonly=False)
    user = fields.Field(
        column_name='Пользователь (ID)',
        attribute='user',
        widget=ForeignKeyWidget(TelegramUser, 'id')
    )
    lightning = fields.Field(
        column_name='Молния',
        attribute='lightning',
        widget=ForeignKeyWidget(Lightning, 'id')
    )
    complete = fields.Field(
        column_name='Успешно',
        attribute='complete',
        widget=BooleanWidget()
    )
    quantity_correct = fields.Field(
        column_name='Процент правильных ответов',
        attribute='quantity_correct',
        widget=IntegerWidget()
    )
    quantity_not_correct = fields.Field(
        column_name='Процент не правильных ответов',
        attribute='quantity_not_correct',
        widget=IntegerWidget()
    )
    created_at = fields.Field(
        column_name='Дата создания',
        attribute='created_at',
    )
    updated_at = fields.Field(
        column_name='Дата обновления',
        attribute='updated_at',
    )

    class Meta:
        model = LightningTest
        fields = (
            'id', 'created_at', 'updated_at', 'user', 'lightning',
            'complete', 'quantity_correct', 'quantity_not_correct'
        )
        export_order = (
            'id', 'created_at', 'updated_at', 'user', 'lightning',
            'complete', 'quantity_correct', 'quantity_not_correct'
        )
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