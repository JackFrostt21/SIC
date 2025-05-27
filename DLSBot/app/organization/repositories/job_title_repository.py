from typing import List, Optional
from app.core.async_utils import AsyncRepository
from app.organization.models import JobTitle


class JobTitleRepository(AsyncRepository[JobTitle]):
    """
    Репозиторий для работы с должностями
    """

    def __init__(self):
        super().__init__(JobTitle)

    async def get_all_job_titles(self) -> List[JobTitle]:
        """
        Получает список всех должностей
        """
        return await self.filter()

    async def get_job_titles_by_department(self, department_id: int) -> List[JobTitle]:
        """
        Получает список должностей для департамента

        :param department_id: ID департамента
        """
        from app.organization.models import Department

        def _get_job_titles():
            try:
                department = Department.objects.get(id=department_id)
                return list(department.job_titles.all())
            except Department.DoesNotExist:
                return []

        from app.core.async_utils import AsyncUnitOfWork

        return await AsyncUnitOfWork.execute(_get_job_titles)

    async def get_job_title_by_id(self, job_title_id: int) -> Optional[JobTitle]:
        """
        Получает должность по ID

        :param job_title_id: ID должности
        :return: Объект должности или None
        """
        return await self.get_by_id(job_title_id)

    async def get_job_title_name(self, job_title_id: int) -> str:
        """
        Получает название должности по ID

        :param job_title_id: ID должности
        :return: Название должности или "Не указано"
        """
        job_title = await self.get_by_id(job_title_id)
        return job_title.name if job_title else "Не указано"
