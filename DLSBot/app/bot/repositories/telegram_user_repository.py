from typing import List, Optional, Dict, Any
from app.core.async_utils import AsyncRepository, AsyncUnitOfWork
from app.bot.models import TelegramUser
from app.organization.models import Company, Department, JobTitle


class TelegramUserRepository(AsyncRepository[TelegramUser]):
    """
    Репозиторий для работы с пользователями Telegram.
    Предоставляет асинхронные методы для основных операций с моделью TelegramUser.
    """
    def __init__(self):
        super().__init__(TelegramUser)
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[TelegramUser]:
        """
        Получает пользователя по его Telegram ID.
        
        :param telegram_id: ID пользователя в Telegram
        :return: Объект пользователя или None, если пользователь не найден
        """
        return await self.get_by_filter(user_id=telegram_id)
    
    async def create_or_update_user(self, 
                                    telegram_id: int, 
                                    **user_data) -> TelegramUser:
        """
        Создает нового пользователя или обновляет существующего.
        
        :param telegram_id: ID пользователя в Telegram
        :param user_data: Данные пользователя для создания/обновления
        :return: Созданный или обновленный объект пользователя
        """
        # Проверяем, существует ли пользователь
        user = await self.get_by_telegram_id(telegram_id)
        
        if user:
            # Обновляем существующего пользователя
            return await self.update(user, **user_data)
        else:
            # Создаем нового пользователя
            user_data['user_id'] = telegram_id
            return await self.create(**user_data)
    
    async def get_users_by_company(self, company_id: int, is_active: bool = True) -> List[TelegramUser]:
        """
        Получает список пользователей для конкретной компании.
        
        :param company_id: ID компании
        :param is_active: Флаг для фильтрации только активных пользователей
        :return: Список пользователей компании
        """
        if is_active:
            return await self.filter(company_id=company_id, state=TelegramUser.STATE_ACTIVE)
        return await self.filter(company_id=company_id)
    
    async def get_users_by_department(self, department_id: int) -> List[TelegramUser]:
        """
        Получает список пользователей для конкретного отдела.
        
        :param department_id: ID отдела
        :return: Список пользователей отдела
        """
        return await self.filter(department_id=department_id)
    
    async def activate_user(self, user_id: int) -> Optional[TelegramUser]:
        """
        Активирует пользователя.
        
        :param user_id: ID пользователя
        :return: Обновленный объект пользователя или None, если пользователь не найден
        """
        user = await self.get_by_id(user_id)
        if user:
            return await self.update(user, state=TelegramUser.STATE_ACTIVE)
        return None
    
    async def deactivate_user(self, user_id: int) -> Optional[TelegramUser]:
        """
        Деактивирует пользователя.
        
        :param user_id: ID пользователя
        :return: Обновленный объект пользователя или None, если пользователь не найден
        """
        user = await self.get_by_id(user_id)
        if user:
            return await self.update(user, state=TelegramUser.STATE_NOT_ACTIVE)
        return None
    
    async def mark_as_deleted(self, user_id: int) -> Optional[TelegramUser]:
        """
        Помечает пользователя как удаленного.
        
        :param user_id: ID пользователя
        :return: Обновленный объект пользователя или None, если пользователь не найден
        """
        user = await self.get_by_id(user_id)
        if user:
            return await self.update(user, state=TelegramUser.STATE_DELETED)
        return None
    
    async def get_or_create_with_company(self, 
                                        telegram_id: int, 
                                        username: str = None, 
                                        full_name: str = None,
                                        company_name: str = None) -> TelegramUser:
        """
        Получает или создает пользователя с привязкой к компании.
        
        :param telegram_id: ID пользователя в Telegram
        :param username: Имя пользователя в Telegram
        :param full_name: Полное имя пользователя
        :param company_name: Название компании
        :return: Объект пользователя
        """
        # Используем транзакцию для атомарной операции
        def _get_or_create_user():
            user, created = TelegramUser.objects.get_or_create(
                user_id=telegram_id,
                defaults={
                    'user_name': username,
                    'full_name': full_name,
                    'state': TelegramUser.STATE_NOT_ACTIVE
                }
            )
            
            # Если передано название компании, привязываем пользователя к компании
            if company_name and not user.company:
                try:
                    company = Company.objects.get(name=company_name)
                    user.company = company
                    user.save(update_fields=['company'])
                except Company.DoesNotExist:
                    pass
                
            return user
            
        return await AsyncUnitOfWork.execute(_get_or_create_user)