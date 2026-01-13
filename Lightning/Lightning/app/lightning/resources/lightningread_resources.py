from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, BooleanWidget
from app.lightning.models import LightningRead, Lightning
from app.bot.models import TelegramUser


class LightningReadResource(resources.ModelResource):
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
    is_read = fields.Field(
        column_name='Прочитано',
        attribute='is_read',
        widget=BooleanWidget()
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
        model = LightningRead
        fields = ('id', 'created_at', 'updated_at', 'user', 'lightning', 'is_read')
        export_order = ('id', 'created_at', 'updated_at', 'user', 'lightning', 'is_read')
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