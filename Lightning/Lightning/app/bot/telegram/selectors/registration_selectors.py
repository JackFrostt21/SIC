from asgiref.sync import sync_to_async
from app.organization.models import Company, Department, JobTitle
from app.bot.models import TelegramUser

@sync_to_async
def get_company_only_list() -> list[Company]:
    return list(Company.objects.only('id', 'name'))


@sync_to_async
def get_department_only_list(company_id: int) -> list[Department]:
    return list(Department.objects.filter(company_id=company_id).only('id', 'name'))


@sync_to_async
def get_job_title_only_list(department_id: int) -> list[JobTitle]:
    return list(JobTitle.objects.filter(departments_of_job_title=department_id).only('id', 'name'))


@sync_to_async
def check_user_status(telegram_id: int) -> int | None:
    try:
        return TelegramUser.objects.only('state').get(telegram_id=telegram_id).state
    except TelegramUser.DoesNotExist:
        return None


@sync_to_async
def _get_company_name(company_id: int | None) -> str | None:
    if not company_id: return None
    return Company.objects.filter(id=company_id).values_list("name", flat=True).first()

@sync_to_async
def _get_department_name(department_id: int | None) -> str | None:
    if not department_id: return None
    return Department.objects.filter(id=department_id).values_list("name", flat=True).first()

@sync_to_async
def _get_job_title_name(job_title_id: int | None) -> str | None:
    if not job_title_id: return None
    return JobTitle.objects.filter(id=job_title_id).values_list("name", flat=True).first()