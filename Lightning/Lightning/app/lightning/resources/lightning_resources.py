from import_export import resources, fields, widgets
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget, BooleanWidget
from app.lightning.models import Lightning
from app.bot.models import TelegramUser, TelegramGroup
from app.organization.models import JobTitle, Department
from django.utils import timezone


class LightningResource(resources.ModelResource):
    # M2M поля
    user = fields.Field(
        column_name='Пользователи (TelegramID через ;)',
        attribute='user',
        widget=ManyToManyWidget(TelegramUser, field='telegram_id', separator=';')  # Исправлено на telegram_id
    )
    group = fields.Field(
        column_name='Группы (названия через ;)',
        attribute='group',
        widget=ManyToManyWidget(TelegramGroup, field='name', separator=';')
    )
    job_titles = fields.Field(
        column_name='Должности (названия через ;)',
        attribute='job_titles',
        widget=ManyToManyWidget(JobTitle, field='name', separator=';')
    )
    department = fields.Field(
        column_name='Подразделения (названия через ;)',
        attribute='department',
        widget=ManyToManyWidget(Department, field='name', separator=';')
    )

    is_draft = fields.Field(column_name='Черновик', attribute='is_draft', widget=widgets.BooleanWidget())
    name = fields.Field(column_name='Молния', attribute='name')
    min_test_percent_course = fields.Field(column_name='Мин. процент теста', attribute='min_test_percent_course')
    content = fields.Field(column_name='Контент', attribute='content')
    image = fields.Field(column_name='Изображение (путь)', attribute='image')
    file = fields.Field(column_name='Файл (путь)', attribute='file')
    id = fields.Field(column_name='ID', attribute='id', readonly=False)

    class Meta:
        model = Lightning
        fields = (
            'id', 'is_draft', 'name', 'min_test_percent_course',
            'user', 'group', 'job_titles', 'department',
            'content', 'image', 'file', 'created_at',
        )
        export_order = (
            'id', 'is_draft', 'name', 'min_test_percent_course',
            'user', 'group', 'job_titles', 'department',
            'content', 'image', 'file', 'created_at',
        )
        import_id_fields = ('id', 'name')  # Добавлен id для поиска
        skip_unchanged = True
        report_skipped = False
        use_transactions = True

    def before_import_row(self, row, **kwargs):
        """
        Обработка строки перед импортом
        """
        # TODO: добавить обработку данных перед импортом
        # Например, проверка существования связанных объектов
        pass

    def before_save_instance(self, instance, row, **kwargs):
        """
        Обработка экземпляра перед сохранением
        """
        # Проверяем обязательное поле name
        if not instance.name:
            raise ValueError("Поле Наименование не может быть пустым")
        
        # Устанавливаем created_at если не указан
        if not instance.created_at:
            instance.created_at = timezone.now()
        
        # Проверяем min_test_percent_course
        if instance.min_test_percent_course is None:
            instance.min_test_percent_course = 0  # значение по умолчанию