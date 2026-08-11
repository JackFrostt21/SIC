from __future__ import annotations

from typing import Any, Dict, Optional

from django.db import transaction

from app.organization.models import Company, Department, JobTitle
from app.bot.models.telegram_user import TelegramUser


def _split_fio(fio: Optional[str]) -> tuple[Optional[str], Optional[str], Optional[str]]:
    if not fio:
        return None, None, None

    parts = [p for p in str(fio).strip().split() if p]
    if not parts:
        return None, None, None

    last_name = parts[0] if len(parts) >= 1 else None
    first_name = parts[1] if len(parts) >= 2 else None
    middle_name = " ".join(parts[2:]) if len(parts) >= 3 else None
    return last_name, first_name, middle_name


def _get_or_create_parent_department(
    *, company: Company, pdiv_id: Optional[str], pdiv_name: Optional[str]
) -> Optional[Department]:
    """
    Апсерт родительского подразделения по идентификатору 1С (pdiv_id).

    Возвращает Department или None, если родителя нет в данных.
    """
    if not pdiv_id:
        return None

    parent, _ = Department.objects.get_or_create(
        company=company,
        source_id=pdiv_id,
        defaults={"name": pdiv_name or ""},
    )

    if pdiv_name and parent.name != pdiv_name:
        parent.name = pdiv_name
        parent.save(update_fields=["name"])

    return parent


def upsert_department(
    *,
    company: Company,
    div_id: str,
    div_name: str,
    pdiv_id: Optional[str],
    pdiv_name: Optional[str],
) -> Department:
    """
    Апсерт подразделения по идентификатору 1С (div_id) внутри компании.

    Также связывает подразделение с родительским, если он присутствует.
    """
    parent = _get_or_create_parent_department(
        company=company, pdiv_id=pdiv_id, pdiv_name=pdiv_name
    )

    dept, _ = Department.objects.get_or_create(
        company=company,
        source_id=div_id,
        defaults={
            "name": div_name or "",
            "parent": parent,
        },
    )

    changed = False
    if div_name and dept.name != div_name:
        dept.name = div_name
        changed = True
    if dept.parent_id != (parent.id if parent else None):
        dept.parent = parent
        changed = True

    if changed:
        dept.save()

    return dept


def upsert_job_title(*, post_id: str, post_name: str, department: Department) -> JobTitle:
    """
    Апсерт должности по идентификатору 1С (post_id) и привязка к департаменту.

    Добавляет связь ManyToMany department.job_titles при отсутствии.
    """
    job, _ = JobTitle.objects.get_or_create(
        source_id=post_id,
        defaults={"name": post_name or ""},
    )

    if post_name and job.name != post_name:
        job.name = post_name
        job.save(update_fields=["name"])

    if department and not department.job_titles.filter(id=job.id).exists():
        department.job_titles.add(job)

    return job


@transaction.atomic
def apply_employee_from_onec(
    *,
    employee: Dict[str, Any],
    company: Optional[Company],
    telegram_id: int,
    username: Optional[str],
    last_name: Optional[str] = None,
    first_name: Optional[str] = None,
    middle_name: Optional[str] = None,
    personal_data_consent: Optional[bool] = None,
) -> TelegramUser:
    """
    Применяет данные сотрудника из внешнего сервиса к объекту TelegramUser.

    - При наличии company/div/post создаёт/обновляет Department и JobTitle.
    - Создаёт/обновляет TelegramUser по telegram_id и переводит в Active.
    - Сохраняет дату рождения в формате YYYY-MM-DD.
    """
    guid = employee.get("id")
    birthday_iso = employee.get("birthday")
    phone = employee.get("phone")
    phone2 = employee.get("phone2")
    email = employee.get("email")

    fio_last_name, fio_first_name, fio_middle_name = _split_fio(employee.get("fio"))
    resolved_last_name = last_name or fio_last_name
    resolved_first_name = first_name or fio_first_name
    resolved_middle_name = middle_name or fio_middle_name

    dept: Optional[Department] = None
    job: Optional[JobTitle] = None

    div_id = employee.get("div_id")
    div_name = employee.get("div")
    pdiv_id = employee.get("pdiv_id")
    pdiv_name = employee.get("pdiv")

    if company and div_id:
        dept = upsert_department(
            company=company,
            div_id=div_id,
            div_name=div_name,
            pdiv_id=pdiv_id,
            pdiv_name=pdiv_name,
        )

    post_id = employee.get("post_id")
    post_name = employee.get("post")
    if dept and post_id:
        job = upsert_job_title(post_id=post_id, post_name=post_name, department=dept)

    user, _ = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "user_name": username,
        },
    )

    if company:
        user.company = company
    if dept:
        user.department = dept
    if job:
        user.job_title = job

    if hasattr(user, "guid_1c"):
        user.guid_1c = guid
    elif hasattr(user, "guid"):
        user.guid = guid

    resolved_full_name = " ".join(
        part for part in [resolved_last_name, resolved_first_name, resolved_middle_name] if part
    ) or employee.get("fio")

    user.user_name = username or user.user_name
    user.full_name = resolved_full_name
    user.last_name = resolved_last_name
    user.first_name = resolved_first_name
    user.middle_name = resolved_middle_name
    user.date_of_birth = birthday_iso
    user.phone = phone

    # игнорируем phone2

    user.email = email
    if personal_data_consent is not None:
        user.personal_data_consent = bool(personal_data_consent)

    if hasattr(TelegramUser, "STATE_ACTIVE"):
        user.state = TelegramUser.STATE_ACTIVE
    elif hasattr(user, "status"):
        setattr(user, "status", 1)

    user.save()

    return user
