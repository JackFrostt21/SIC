from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import TelegramUser, TelegramGroup
from app.organization.models import Company, Department, JobTitle


class TelegramUserResource(resources.ModelResource):
    """
    Ресурс для импорта/экспорта пользователей Telegram
    """

    # Настройка полей с внешними ключами
    company = fields.Field(
        column_name="company",
        attribute="company",
        widget=ForeignKeyWidget(Company, "name"),
    )

    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=ForeignKeyWidget(Department, "name"),
    )

    job_title = fields.Field(
        column_name="job_title",
        attribute="job_title",
        widget=ForeignKeyWidget(JobTitle, "name"),
    )

    class Meta:
        model = TelegramUser
        fields = (
            "id",
            "telegram_id",
            "user_name",
            "full_name",
            "last_name",
            "first_name",
            "middle_name",
            "date_of_birth",
            "phone",
            "email",
            "language",
            "company",
            "department",
            "job_title",
            "state",
            "is_actual",
        )
        export_order = (
            "id",
            "telegram_id",
            "user_name",
            "full_name",
            "last_name",
            "first_name",
            "middle_name",
            "date_of_birth",
            "phone",
            "email",
            "language",
            "company",
            "department",
            "job_title",
            "state",
            "is_actual",
        )
        import_id_fields = (
            "telegram_id",
        )  # Используем telegram_id как уникальный идентификатор
        skip_unchanged = True
        report_skipped = False

    def get_export_headers(self, **kwargs):
        """
        Переопределение заголовков для экспорта
        """
        headers = super().get_export_headers(**kwargs)
        # Заменяем технические названия на понятные
        header_mapping = {
            "telegram_id": "Telegram ID",
            "user_name": "Username",
            "full_name": "ФИО",
            "last_name": "Фамилия",
            "first_name": "Имя",
            "middle_name": "Отчество",
            "date_of_birth": "Дата рождения",
            "phone": "Телефон",
            "email": "Email",
            "language": "Язык",
            "company": "Компания",
            "department": "Подразделение",
            "job_title": "Должность",
            "state": "Статус",
            "is_actual": "Актуальный",
        }

        return [header_mapping.get(header, header) for header in headers]

    def before_import_row(self, row, **kwargs):
        """
        Обработка строки перед импортом
        """
        # Обработка ФИО
        if "full_name" in row and row["full_name"]:
            row["full_name"] = str(row["full_name"]).strip()

        # Обработка отдельных полей имени
        for field in ["last_name", "first_name", "middle_name", "user_name"]:
            if field in row and row[field]:
                row[field] = str(row[field]).strip()

        # Обработка email
        if "email" in row and row["email"]:
            row["email"] = str(row["email"]).strip().lower()

        # Обработка телефона
        if "phone" in row and row["phone"]:
            # Убираем все кроме цифр и + в начале
            phone = str(row["phone"]).strip()
            if phone and not phone.startswith("+"):
                phone = "+" + phone
            row["phone"] = phone

    def before_save_instance(self, instance, using_transactions, dry_run):
        """
        Обработка экземпляра перед сохранением
        """
        # Проверяем обязательные поля
        if not instance.telegram_id:
            raise ValueError("Telegram ID является обязательным полем")

        # Валидация email
        if instance.email:
            import re

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, instance.email):
                raise ValueError(f"Некорректный email: {instance.email}")

    def get_instance(self, instance_loader, row):
        """
        Переопределение получения экземпляра для обновления существующих записей
        """
        try:
            return TelegramUser.objects.get(
                telegram_id=row.get("telegram_id") or row.get("Telegram ID")
            )
        except TelegramUser.DoesNotExist:
            return None


class TelegramGroupResource(resources.ModelResource):
    """
    Ресурс для импорта/экспорта групп пользователей Telegram
    """

    class Meta:
        model = TelegramGroup
        fields = ("id", "name", "description")
        export_order = ("id", "name", "description")
        import_id_fields = ("id",)
        skip_unchanged = True
        report_skipped = False

    def before_import_row(self, row, **kwargs):
        """
        Обработка строки перед импортом
        """
        if "name" in row:
            row["name"] = str(row["name"]).strip()

        if "description" in row and row["description"]:
            row["description"] = str(row["description"]).strip()

    def before_save_instance(self, instance, using_transactions, dry_run):
        """
        Обработка экземпляра перед сохранением
        """
        if not instance.name:
            raise ValueError("Название группы не может быть пустым")
