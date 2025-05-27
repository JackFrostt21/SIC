from typing import List, Dict, Any, Optional
from app.bot.repositories.telegram_group_repository import TelegramGroupRepository
from app.bot.repositories.telegram_user_repository import TelegramUserRepository
from app.bot.models import TelegramGroup


class TelegramGroupService:
    """
    Сервис для работы с группами пользователей Telegram.
    Содержит бизнес-логику управления группами.
    """
    def __init__(self):
        self.group_repository = TelegramGroupRepository()
        self.user_repository = TelegramUserRepository()
    
    async def create_group(self, name: str, description: str = None) -> Dict[str, Any]:
        """
        Создает новую группу пользователей.
        
        :param name: Название группы
        :param description: Описание группы
        :return: Словарь с результатом операции
        """
        # Проверяем, существует ли группа с таким именем
        existing_group = await self.group_repository.get_by_name(name)
        
        if existing_group:
            return {
                "success": False,
                "message": "Группа с таким названием уже существует"
            }
        
        # Создаем новую группу
        new_group = await self.group_repository.create(name=name, description=description)
        
        return {
            "success": True,
            "group": new_group,
            "message": "Группа успешно создана"
        }
    
    async def update_group(self, group_id: int, name: str = None, description: str = None) -> Dict[str, Any]:
        """
        Обновляет информацию о группе.
        
        :param group_id: ID группы
        :param name: Новое название группы
        :param description: Новое описание группы
        :return: Словарь с результатом операции
        """
        group = await self.group_repository.get_by_id(group_id)
        
        if not group:
            return {
                "success": False,
                "message": "Группа не найдена"
            }
        
        # Создаем словарь с данными для обновления
        update_data = {}
        if name:
            update_data['name'] = name
        if description is not None:  # Позволяем устанавливать пустое описание
            update_data['description'] = description
        
        # Если нет данных для обновления, возвращаем успех без изменений
        if not update_data:
            return {
                "success": True,
                "group": group,
                "message": "Нет данных для обновления"
            }
        
        # Обновляем группу
        updated_group = await self.group_repository.update(group, **update_data)
        
        return {
            "success": True,
            "group": updated_group,
            "message": "Информация о группе обновлена"
        }
    
    async def delete_group(self, group_id: int) -> Dict[str, Any]:
        """
        Удаляет группу.
        
        :param group_id: ID группы
        :return: Словарь с результатом операции
        """
        group = await self.group_repository.get_by_id(group_id)
        
        if not group:
            return {
                "success": False,
                "message": "Группа не найдена"
            }
        
        # Удаляем группу
        await self.group_repository.delete(group)
        
        return {
            "success": True,
            "message": "Группа успешно удалена"
        }
    
    async def add_users_to_group(self, group_id: int, telegram_ids: List[int]) -> Dict[str, Any]:
        """
        Добавляет пользователей в группу по их Telegram ID.
        
        :param group_id: ID группы
        :param telegram_ids: Список Telegram ID пользователей
        :return: Словарь с результатом операции
        """
        group = await self.group_repository.get_by_id(group_id)
        
        if not group:
            return {
                "success": False,
                "message": "Группа не найдена"
            }
        
        # Получаем ID пользователей из базы данных
        user_ids = []
        for telegram_id in telegram_ids:
            user = await self.user_repository.get_by_telegram_id(telegram_id)
            if user:
                user_ids.append(user.id)
        
        if not user_ids:
            return {
                "success": False,
                "message": "Не найдено пользователей для добавления в группу"
            }
        
        # Добавляем пользователей в группу
        updated_group = await self.group_repository.add_users_to_group(group_id, user_ids)
        
        return {
            "success": True,
            "group": updated_group,
            "added_count": len(user_ids),
            "message": f"Добавлено {len(user_ids)} пользователей в группу"
        }
    
    async def remove_users_from_group(self, group_id: int, telegram_ids: List[int]) -> Dict[str, Any]:
        """
        Удаляет пользователей из группы по их Telegram ID.
        
        :param group_id: ID группы
        :param telegram_ids: Список Telegram ID пользователей
        :return: Словарь с результатом операции
        """
        group = await self.group_repository.get_by_id(group_id)
        
        if not group:
            return {
                "success": False,
                "message": "Группа не найдена"
            }
        
        # Получаем ID пользователей из базы данных
        user_ids = []
        for telegram_id in telegram_ids:
            user = await self.user_repository.get_by_telegram_id(telegram_id)
            if user:
                user_ids.append(user.id)
        
        if not user_ids:
            return {
                "success": False,
                "message": "Не найдено пользователей для удаления из группы"
            }
        
        # Удаляем пользователей из группы
        updated_group = await self.group_repository.remove_users_from_group(group_id, user_ids)
        
        return {
            "success": True,
            "group": updated_group,
            "removed_count": len(user_ids),
            "message": f"Удалено {len(user_ids)} пользователей из группы"
        }
    
    async def get_group_users(self, group_id: int) -> Dict[str, Any]:
        """
        Получает список пользователей группы.
        
        :param group_id: ID группы
        :return: Словарь с результатом операции
        """
        group = await self.group_repository.get_by_id(group_id)
        
        if not group:
            return {
                "success": False,
                "message": "Группа не найдена"
            }
        
        # Получаем пользователей группы
        users = await self.group_repository.get_users_in_group(group_id)
        
        return {
            "success": True,
            "group": {
                "id": group.id,
                "name": group.name,
                "description": group.description
            },
            "users": [
                {
                    "id": user.id,
                    "telegram_id": user.user_id,
                    "full_name": user.full_name,
                    "username": user.user_name
                }
                for user in users
            ],
            "users_count": len(users)
        }