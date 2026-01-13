from import_export import resources, fields, widgets
from import_export.widgets import ForeignKeyWidget
from ..models import TelegramUser, RowStateModel
from ...organization.models import Company, Department, JobTitle
from datetime import datetime, date


class DateStringWidget(widgets.Widget):
    def __init__(self, input_formats=None, output_format="%Y-%m-%d"):
        self.input_formats = input_formats or [
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
        ]
        self.output_format = output_format

    def clean(self, value, row=None, *args, **kwargs):
        if value is None or value == "":
            return None

        if isinstance(value, datetime):
            return value.date().strftime(self.output_format)
        if isinstance(value, date):
            return value.strftime(self.output_format)

        if isinstance(value, str):
            s = value.strip()
            for fmt in self.input_formats:
                try:
                    return datetime.strptime(s, fmt).strftime(self.output_format)
                except ValueError:
                    continue
            raise ValueError(f"Неверный формат даты: '{value}'")

        return str(value)

    def render(self, value, obj=None):
        if value is None or value == "":
            return ""
        if isinstance(value, datetime):
            return value.date().strftime(self.output_format)
        if isinstance(value, date):
            return value.strftime(self.output_format)
        if isinstance(value, str):
            s = value.strip()
            # Предполагаем, что строка уже в нужном формате, если парсинг не удастся
            for fmt in self.input_formats:
                try:
                    return datetime.strptime(s, fmt).strftime(self.output_format)
                except ValueError:
                    continue
            return s
        return str(value)


class StateWidget(widgets.Widget):
    def clean(self, value, row=None, *args, **kwargs):
        if value is None or value == "":
            return None

        allowed_states = {
            RowStateModel.STATE_NOT_ACTIVE,
            RowStateModel.STATE_ACTIVE,
            RowStateModel.STATE_DELETED,
            RowStateModel.STATE_NEED_CONFIRMATION,
        }

        # Прямо число
        if isinstance(value, int):
            if value in allowed_states:
                return value
            raise ValueError(f"Недопустимое значение статуса: {value}")

        # Числовая строка
        if isinstance(value, str):
            s = value.strip()
            if s.isdigit():
                iv = int(s)
                if iv in allowed_states:
                    return iv
                raise ValueError(f"Недопустимое значение статуса: {s}")
            raise ValueError(
                f"Ожидалось числовое значение статуса, получено: '{value}'"
            )

        # Прочие числовые типы, приводимые к int
        try:
            iv = int(value)
            if iv in allowed_states:
                return iv
            raise ValueError(f"Недопустимое значение статуса: {iv}")
        except Exception:
            raise ValueError(
                f"Ожидалось числовое значение статуса, получено: '{value}'"
            )


class TelegramUserResource(resources.ModelResource):
    id = fields.Field(column_name="ID", attribute="id", readonly=False)

    # настройка полей с внешними ключами
    company = fields.Field(
        column_name="company",
        attribute="company",
        widget=ForeignKeyWidget(Company, "id"),
    )
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=ForeignKeyWidget(Department, "id"),
    )
    job_title = fields.Field(
        column_name="job_title",
        attribute="job_title",
        widget=ForeignKeyWidget(JobTitle, "id"),
    )
    state = fields.Field(column_name="state", attribute="state", widget=StateWidget())
    # Основные поля
    user_id = fields.Field(
        column_name="telegram_id",
        attribute="telegram_id",
    )
    username = fields.Field(
        column_name="username",
        attribute="username",
    )
    full_name = fields.Field(
        column_name="full_name",
        attribute="full_name",
    )
    last_name = fields.Field(
        column_name="last_name",
        attribute="last_name",
    )
    first_name = fields.Field(
        column_name="first_name",
        attribute="first_name",
    )
    middle_name = fields.Field(
        column_name="middle_name",
        attribute="middle_name",
    )
    date_of_birth = fields.Field(
        column_name="date_of_birth",
        attribute="date_of_birth",
        widget=DateStringWidget(output_format="%Y-%m-%d"),
    )
    phone = fields.Field(
        column_name="phone",
        attribute="phone",
    )
    email = fields.Field(
        column_name="email",
        attribute="email",
    )
    last_activity = fields.Field(
        column_name="last_activity",
        attribute="last_activity",
    )
    language = fields.Field(
        column_name="language",
        attribute="language",
    )
    image = fields.Field(
        column_name="image",
        attribute="image",
    )

    class Meta:
        model = TelegramUser
        fields = (
            "id",
            "telegram_id",
            "username",
            "full_name",
            "last_name",
            "first_name",
            "middle_name",
            "date_of_birth",
            "phone",
            "email",
            "last_activity",
            "language",
            "company",
            "department",
            "job_title",
            "state",
            "image",
        )
        export_order = (
            "id",
            "telegram_id",
            "username",
            "full_name",
            "last_name",
            "first_name",
            "middle_name",
            "date_of_birth",
            "phone",
            "email",
            "last_activity",
            "language",
            "company",
            "department",
            "job_title",
            "state",
            "image",
        )
        import_id_fields = ("id", "telegram_id")
        skip_unchanged = True
        report_skipped = False
        use_transactions = True

    def before_import_row(self, row, row_number=None, **kwargs):
        # Поддержка обоих заголовков: если пришёл 'Статус', маппим в 'state'
        if "state" not in row and "Статус" in row:
            row["state"] = row["Статус"]

    def before_save_instance(self, instance, row, **kwargs):
        """
        Обработка экземпляра перед сохранением
        """
        # Проверяем обязательное поле user_id
        if not instance.telegram_id:
            raise ValueError("Поле Telegram ID не может быть пустым")
