from typing import List, Optional, Dict, Any
from app.core.async_utils import AsyncRepository, AsyncUnitOfWork
from app.organization.models import Department


class DepartmentRepository(AsyncRepository[Department]):
    """
    Репозиторий для работы с департаментами
    """

    def __init__(self):
        super().__init__(Department)

    async def get_departments_by_company(self, company_id: int) -> List[Department]:
        """
        Получает список департаментов для компании

        :param company_id: ID компании
        :return: Список департаментов
        """
        return await self.filter(company_id=company_id)

    async def get_department_by_id(self, department_id: int) -> Optional[Department]:
        """
        Получает департамент по ID

        :param department_id: ID департамента
        :return: Объект департамента или None
        """
        return await self.get_by_id(department_id)

    async def get_department_name(self, department_id: int) -> str:
        """
        Получает название департамента по ID

        :param department_id: ID департамента
        :return: Название департамента или "Не указано"
        """
        department = await self.get_by_id(department_id)
        return department.name if department else "Не указано"

    async def get_department_with_job_titles(
        self, department_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получает департамент вместе с должностями

        :param department_id: ID департамента
        :return: Словарь с департаментом и должностями
        """

        def _get_department_with_job_titles():
            try:
                department = Department.objects.get(id=department_id)
                job_titles = list(department.job_titles.all())

                return {"department": department, "job_titles": job_titles}
            except Department.DoesNotExist:
                return None

        return await AsyncUnitOfWork.execute(_get_department_with_job_titles)
