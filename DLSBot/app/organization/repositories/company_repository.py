from typing import List, Optional, Dict, Any
from django.conf import (
    settings,
)
import os
from app.core.async_utils import AsyncRepository, AsyncUnitOfWork
from app.organization.models import Company, SettingsBot


class CompanyRepository(AsyncRepository[Company]):
    """
    Репозиторий для работы с компаниями
    """

    def __init__(self):
        super().__init__(Company)

    async def get_all_companies(self) -> List[Company]:
        """
        Получает список всех компаний

        :return: Список компаний
        """
        return await self.filter()

    async def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """
        Получает компанию по ID

        :param company_id: ID компании
        :return: Объект компании или None
        """
        return await self.get_by_id(company_id)

    async def get_company_name(self, company_id: int) -> str:
        """
        Получает название компании по ID

        :param company_id: ID компании
        :return: Название компании или "Не указано"
        """
        company = await self.get_by_id(company_id)
        return company.name if company else "Не указано"


class SettingsBotRepository(AsyncRepository[SettingsBot]):
    """
    Репозиторий для работы с настройками бота
    """

    def __init__(self):
        super().__init__(SettingsBot)

    async def get_settings_by_company(self, company_id: int) -> Optional[SettingsBot]:
        """
        Получает настройки бота для компании

        :param company_id: ID компании
        :return: Объект настроек или None
        """
        return await self.get_by_filter(company_id=company_id)

    async def get_first_settings(self) -> Optional[SettingsBot]:
        """
        Получает первые доступные настройки бота (например, общие, если нет для компании).
        Или просто самые первые в таблице, если нет company_id.
        """
        # Я беру первые настройки из всех.
        settings_list = await self.filter()  # Может вернуть несколько, если нет фильтра # TODO: переделать

        settings_obj = (
            await self.model_class.objects.afirst()
        )
        return settings_obj if settings_obj else None

    async def get_list_courses_image_path(
        self, company_id: Optional[int] = None
    ) -> Optional[str]:
        """
        Получает путь к изображению для списка курсов.
        Сначала пытается найти настройки для указанной компании, потом общие.

        :param company_id: ID компании (опционально).
        :return: Путь к изображению или None.
        """
        settings = None
        if company_id:
            settings = await self.get_settings_by_company(company_id=company_id)

        if not settings:
            settings = await self.get_first_settings()

        if not settings:
            return None

        if settings.image_list_courses and hasattr(settings.image_list_courses, "path"):
            # Убедимся, что файл существует перед возвратом пути
            if os.path.exists(settings.image_list_courses.path):
                return settings.image_list_courses.path
            else:

                pass  # TODO: Или вернуть None, или не проверять os.path.exists, если доверяем Django
        return None

    async def get_start_image_path(
        self, company_id: Optional[int] = None
    ) -> Optional[str]:
        """
        Получает путь к стартовому изображению

        :param company_id: ID компании (опционально)
        :return: Путь к изображению или None
        """
        settings = None

        if company_id:
            settings = await self.get_by_filter(company_id=company_id)

        if not settings:
            settings = await self.get_first_settings()

        if settings and settings.image_start:
            return settings.image_start.path

        return None

    async def get_test_result_image_path(
        self, passed: bool, company_id: Optional[int] = None
    ) -> Optional[str]:
        """
        Возвращает путь к изображению в зависимости от результата теста.
        Сначала пытается найти настройки для указанной компании, потом общие.

        :param passed: True, если тест сдан, иначе False.
        :param company_id: ID компании (опционально).
        :return: Путь к изображению или None.
        """
        settings = None
        if company_id:
            settings = await self.get_settings_by_company(company_id=company_id)

        if not settings:
            # Если для компании нет настроек или company_id не был передан, берем первые/общие
            settings = await self.get_first_settings()

        if not settings:
            return None

        image_field_name = "image_test_success" if passed else "image_test_fail"
        image_file = getattr(settings, image_field_name, None)

        if image_file and hasattr(image_file, "path"):
            return image_file.path
        return None

    async def get_url_web_app(self, company_id: Optional[int] = None) -> Optional[str]:
        """
        Получает базовый URL для WebApp.
        Сначала пытается найти настройки для указанной компании, потом общие.

        :param company_id: ID компании (опционально).
        :return: Строку с URL или None.
        """
        settings = None
        if company_id:
            settings = await self.get_settings_by_company(company_id=company_id)

        if not settings:
            settings = await self.get_first_settings()

        if settings and settings.url_web_app:
            return str(settings.url_web_app)  # Возвращаем как строку

        return None
