from typing import List, Optional, Dict, Any
from datetime import datetime
from app.bot.repositories.telegram_user_repository import TelegramUserRepository
from app.bot.repositories.telegram_group_repository import TelegramGroupRepository
from app.bot.models import TelegramUser
from app.organization.models import Company


class TelegramUserService:
    """
    Сервис для работы с пользователями Telegram.
    Содержит бизнес-логику обработки пользователей.
    """
    def __init__(self):
        self.user_repository = TelegramUserRepository()
        self.group_repository = TelegramGroupRepository()
    
    async def register_user(self, 
                           telegram_id: int, 
                           username: str = None, 
                           full_name: str = None,
                           **user_data) -> Dict[str, Any]:
        """
        Регистрирует нового пользователя или обновляет существующего.
        
        :param telegram_id: ID пользователя в Telegram
        :param username: Имя пользователя в Telegram
        :param full_name: Полное имя пользователя
        :param user_data: Дополнительные данные пользователя
        :return: Словарь с результатами регистрации
        """
        # Проверяем, существует ли пользователь
        existing_user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if existing_user:
            # Обновляем данные существующего пользователя
            if username and not existing_user.user_name:
                user_data['user_name'] = username
            
            if full_name and not existing_user.full_name:
                user_data['full_name'] = full_name
            
            # Обновляем только если есть данные для обновления
            if user_data:
                updated_user = await self.user_repository.update(existing_user, **user_data)
                return {
                    "success": True,
                    "user": updated_user,
                    "is_new": False,
                    "message": "Данные пользователя обновлены"
                }
            
            return {
                "success": True,
                "user": existing_user,
                "is_new": False,
                "message": "Пользователь уже зарегистрирован"
            }
        else:
            # Создаем нового пользователя
            user_data.update({
                'user_id': telegram_id,
                'user_name': username,
                'full_name': full_name,
                'state': TelegramUser.STATE_NOT_ACTIVE
            })
            
            new_user = await self.user_repository.create(**user_data)
            return {
                "success": True,
                "user": new_user,
                "is_new": True,
                "message": "Пользователь успешно зарегистрирован"
            }
    
    async def get_user_info(self, telegram_id: int) -> Dict[str, Any]:
        """
        Получает информацию о пользователе.
        
        :param telegram_id: ID пользователя в Telegram
        :return: Словарь с информацией о пользователе
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Получаем группы пользователя
        groups = await self.group_repository.get_groups_for_user(user.id)
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "telegram_id": user.user_id,
                "username": user.user_name,
                "full_name": user.full_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": user.middle_name,
                "email": user.email,
                "phone": user.phone,
                "date_of_birth": user.date_of_birth,
                "status": user.get_state_display(),
                "company": user.company.name if user.company else None,
                "department": user.department.name if user.department else None,
                "job_title": user.job_title.name if user.job_title else None,
                "groups": [{"id": g.id, "name": g.name} for g in groups],
                "is_active": user.state == TelegramUser.STATE_ACTIVE
            }
        }
    
    async def update_user_status(self, telegram_id: int, status: int) -> Dict[str, Any]:
        """
        Обновляет статус пользователя.
        
        :param telegram_id: ID пользователя в Telegram
        :param status: Новый статус пользователя (STATE_ACTIVE, STATE_NOT_ACTIVE, STATE_DELETED)
        :return: Словарь с результатом операции
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Проверяем, что статус валидный
        if status not in [TelegramUser.STATE_ACTIVE, TelegramUser.STATE_NOT_ACTIVE, TelegramUser.STATE_DELETED]:
            return {
                "success": False,
                "message": "Некорректный статус"
            }
        
        # Обновляем статус
        updated_user = await self.user_repository.update(user, state=status)
        
        return {
            "success": True,
            "user": updated_user,
            "message": f"Статус пользователя обновлен на '{updated_user.get_state_display()}'"
        }
    
    async def assign_to_company(self, telegram_id: int, company_id: int) -> Dict[str, Any]:
        """
        Привязывает пользователя к компании.
        
        :param telegram_id: ID пользователя в Telegram
        :param company_id: ID компании
        :return: Словарь с результатом операции
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Обновляем компанию
        updated_user = await self.user_repository.update(user, company_id=company_id)
        
        return {
            "success": True,
            "user": updated_user,
            "message": "Пользователь привязан к компании"
        }
    
    async def update_user_profile(self, 
                               telegram_id: int, 
                               **profile_data) -> Dict[str, Any]:
        """
        Обновляет профиль пользователя.
        
        :param telegram_id: ID пользователя в Telegram
        :param profile_data: Данные профиля для обновления
        :return: Словарь с результатом операции
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Валидируем и фильтруем данные
        valid_fields = [
            'full_name', 'first_name', 'last_name', 'middle_name',
            'phone', 'email', 'date_of_birth', 'department_id', 'job_title_id'
        ]
        
        filtered_data = {k: v for k, v in profile_data.items() if k in valid_fields}
        
        # Обновляем пользователя
        updated_user = await self.user_repository.update(user, **filtered_data)
        
        return {
            "success": True,
            "user": updated_user,
            "message": "Профиль пользователя обновлен"
        }