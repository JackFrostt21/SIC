from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from ..models import TelegramGroup
from ..models import TelegramUser


class TelegramGroupResource(resources.ModelResource):
    users = fields.Field(
        column_name='Пользователи (username через ;)',
        attribute='users',
        widget=ManyToManyWidget(TelegramUser, field='username', separator=';')
    )
    name = fields.Field(
        column_name='Наименование группы',
        attribute='name',
    )

    class Meta:
        model = TelegramGroup
        fields = (
            'name',
            'users',
        )
        export_order = (
            'name',
            'users',
        )
        import_id_fields = ('name',)
        skip_unchanged = True
        report_skipped = False
        use_transactions = True
    
    def before_import_row(self, row, **kwargs):
        """
        Обработка строки перед импортом
        """
        pass # TODO: добавить обработку данных перед импортом

    def before_save_instance(self, instance, using_transactions=True, dry_run=False):
        """
        Обработка экземпляра перед сохранением
        """
        #Проверяем обязательное поле name
        if not instance.name:
            raise ValueError("Поле Наименование группы не может быть пустым")