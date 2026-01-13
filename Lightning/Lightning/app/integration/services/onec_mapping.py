from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from django.db import transaction

from app.organization.models.company_models import Company, Department, JobTitle
from app.bot.models.telegramuser_models import TelegramUser


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

    dept, created = Department.objects.get_or_create(
        company=company,
        source_id=div_id,
        defaults={
            "name": div_name or "",
            "parent": parent,
        },
    )
    # Обновим имя и parent при необходимости
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


def upsert_job_title(
    *, post_id: str, post_name: str, department: Department
) -> JobTitle:
    """
    Апсерт должности по идентификатору 1С (post_id) и привязка к департаменту.

    Добавляет связь ManyToMany department.job_titles при отсутствии.
    """
    job, created = JobTitle.objects.get_or_create(
        source_id=post_id,
        defaults={"name": post_name or ""},
    )
    # Синхронизируем имя при необходимости
    if post_name and job.name != post_name:
        job.name = post_name
        job.save(update_fields=["name"])

    # Поддержим ManyToMany связь department.job_titles, чтобы должность была видна в отделе
    if department and not department.job_titles.filter(id=job.id).exists():
        department.job_titles.add(job)

    return job


@transaction.atomic
def apply_employee_from_onec(
    *,
    employee: Dict[str, Any],
    company: Company,
    telegram_id: int,
    username: Optional[str],
    last_name: str,
    first_name: str,
    middle_name: Optional[str],
) -> TelegramUser:
    """
    Применяет данные сотрудника из 1С к объекту TelegramUser.

    - Создаёт/обновляет Department (и родителя).
    - Создаёт/обновляет JobTitle и привязывает к Department.
    - Создаёт/обновляет TelegramUser по telegram_id, ставит Active.
    - Сохраняет дату рождения в формате YYYY-MM-DD.
    """
    guid = employee.get("id")
    birthday_iso = employee.get("birthday")  # YYYY-MM-DD ожидаемо
    phone = employee.get("phone")
    phone2 = employee.get("phone2")
    email = employee.get("email")
    status = employee.get(
        "status",
        TelegramUser.STATE_ACTIVE if hasattr(TelegramUser, "STATE_ACTIVE") else 1,
    )

    div_id = employee.get("div_id")
    div_name = employee.get("div")
    pdiv_id = employee.get("pdiv_id")
    pdiv_name = employee.get("pdiv")

    dept = upsert_department(
        company=company,
        div_id=div_id,
        div_name=div_name,
        pdiv_id=pdiv_id,
        pdiv_name=pdiv_name,
    )

    post_id = employee.get("post_id")
    post_name = employee.get("post")
    job = upsert_job_title(post_id=post_id, post_name=post_name, department=dept)

    # Получаем или создаём пользователя по telegram_id
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": username,
        },
    )

    # Заполняем атрибуты (статус Active по бизнес-правилу)
    user.company = company
    user.department = dept
    user.job_title = job
    if hasattr(user, "guid_1c"):
        user.guid_1c = guid
    elif hasattr(user, "guid"):
        user.guid = guid
    user.last_name = last_name
    user.first_name = first_name
    user.middle_name = middle_name
    user.date_of_birth = birthday_iso  # храним YYYY-MM-DD
    user.phone = phone
    if hasattr(user, "phone2"):
        setattr(user, "phone2", phone2)
    user.email = email
    if hasattr(TelegramUser, "STATE_ACTIVE"):
        user.state = TelegramUser.STATE_ACTIVE
    elif hasattr(user, "status"):
        setattr(user, "status", 1)
    user.save()

    return user
