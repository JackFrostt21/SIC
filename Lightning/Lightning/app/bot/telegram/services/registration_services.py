import re
from datetime import date, datetime
from app.bot.models.telegramuser_models import TelegramUser
from asgiref.sync import sync_to_async

# Ограничения для даты рождения
MIN_AGE = 14
MAX_AGE = 100
MIN_YEAR = 1900

# Только кириллица
CYRILLIC_PATTERN = re.compile(r"^[\u0400-\u04FF]+(?:[ -][\u0400-\u04FF]+)*$")


# Валидатор для кириллицы
def is_cyrillic(text: str) -> bool:
    return bool(CYRILLIC_PATTERN.match(text or ""))


# Нормализация имени
def normalize_person_name(text: str) -> str:
    """
    Нормализуем регистр: 'ИВАНОВ-ПЕТРОВ' -> 'Иванов-Петров', '  анна  мария  ' -> 'Анна Мария'
    """
    s = (text or "").strip()
    s = re.sub(r"\s+", " ", s)  # схлопываем множественные пробелы
    s = re.sub(r"\s*-\s*", "-", s)  # вокруг дефиса убираем пробелы
    parts = re.split(r"([- ])", s)  # оставляем разделители
    return "".join(p.capitalize() if p not in {"-", " "} else p for p in parts)


# Валидатор для даты рождения
def parse_birth_date(birth_date: str) -> date | None:
    """
    Принимает строку, вытаскивает цифры, ожидает DDMMYYYY.
    Возвращает date или None если невалидно.
    """
    digits = re.sub(r"\D", "", birth_date or "")
    if len(digits) != 8:
        return None

    day = int(digits[0:2])
    month = int(digits[2:4])
    year = int(digits[4:8])

    # Базовая проверка корректности календарной даты
    try:
        d = date(year, month, day)
    except ValueError:
        return None

    today = date.today()

    # Не из будущего и не слишком старая (по году)
    if d > today or year < MIN_YEAR:
        return None

    # Проверка возраста
    age = (today.year - d.year) - ((today.month, today.day) < (d.month, d.day))
    if age < MIN_AGE or age > MAX_AGE:
        return None

    return d


# Валидатор для email
def is_valid_email(email: str) -> bool:
    return bool(
        re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email or "")
    )


def _compose_full_name(
    last_name: str | None, first_name: str | None, middle_name: str | None
) -> str:
    parts = [p for p in [last_name, first_name, middle_name] if p]
    return " ".join(parts)


@sync_to_async
def upsert_telegram_user(data: dict) -> None:
    """
    Создаёт/обновляет TelegramUser и ставит статус NEED_CONFIRMATION.
    Ожидает в data: telegram_id, username, last_name, first_name, middle_name,
                    date_of_birth (DD.MM.YYYY), phone, email,
                    company (id), department (id), job_title (id)
    """
    full_name = _compose_full_name(
        data.get("surname"), data.get("name"), data.get("patronymic")
    )

    # Преобразуем дату рождения в ISO-формат YYYY-MM-DD для хранения
    birth_date_raw = data.get("birth_date")
    birth_date_iso = None
    if birth_date_raw:
        try:
            if isinstance(birth_date_raw, date):
                birth_date_iso = birth_date_raw.strftime("%Y-%m-%d")
            else:
                # ожидаем строку вида DD.MM.YYYY — конвертируем в YYYY-MM-DD
                birth_date_iso = datetime.strptime(
                    str(birth_date_raw), "%d.%m.%Y"
                ).strftime("%Y-%m-%d")
        except Exception:
            birth_date_iso = None

    TelegramUser.objects.update_or_create(
        telegram_id=data["telegram_id"],
        defaults={
            "username": data.get("username"),
            "company_id": data.get("company"),
            "department_id": data.get("department"),
            "job_title_id": data.get("job_title"),
            "full_name": full_name or None,
            "last_name": data.get("surname") or None,
            "first_name": data.get("name") or None,
            "middle_name": data.get("patronymic") or None,
            "date_of_birth": birth_date_iso,
            "phone": data.get("phone") or None,
            "email": data.get("email") or None,
            "state": TelegramUser.STATE_NEED_CONFIRMATION,
            "language": "ru",
        },
    )
