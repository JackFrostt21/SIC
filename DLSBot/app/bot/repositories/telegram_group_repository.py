from typing import List, Optional, Set
from app.core.async_utils import AsyncRepository, AsyncUnitOfWork
from app.bot.models import TelegramGroup, TelegramUser


class TelegramGroupRepository(AsyncRepository[TelegramGroup]):
    """
    Репозиторий для работы с группами пользователей Telegram.
    Предоставляет асинхронные методы для операций с моделью TelegramGroup.
    """
    def __init__(self):
        super().__init__(TelegramGroup)
    
    async def get_by_name(self, name: str) -> Optional[TelegramGroup]:
        """
        Получает группу по её названию.
        
        :param name: Название группы
        :return: Объект группы или None, если группа не найдена
        """
        return await self.get_by_filter(name=name)
    
    async def add_users_to_group(self, group_id: int, user_ids: List[int]) -> Optional[TelegramGroup]:
        """
        Добавляет пользователей в группу.
        
        :param group_id: ID группы
        :param user_ids: Список ID пользователей для добавления
        :return: Обновленный объект группы или None, если группа не найдена
        """
        def _add_users():
            try:
                group = TelegramGroup.objects.get(id=group_id)
                users = TelegramUser.objects.filter(id__in=user_ids)
                
                # Добавляем пользователей в группу
                group.users.add(*users)
                
                return group
            except TelegramGroup.DoesNotExist:
                return None
        
        return await AsyncUnitOfWork.execute(_add_users)
    
    async def remove_users_from_group(self, group_id: int, user_ids: List[int]) -> Optional[TelegramGroup]:
        """
        Удаляет пользователей из группы.
        
        :param group_id: ID группы
        :param user_ids: Список ID пользователей для удаления
        :return: Обновленный объект группы или None, если группа не найдена
        """
        def _remove_users():
            try:
                group = TelegramGroup.objects.get(id=group_id)
                users = TelegramUser.objects.filter(id__in=user_ids)
                
                # Удаляем пользователей из группы
                group.users.remove(*users)
                
                return group
            except TelegramGroup.DoesNotExist:
                return None
        
        return await AsyncUnitOfWork.execute(_remove_users)
    
    async def get_users_in_group(self, group_id: int) -> List[TelegramUser]:
        """
        Получает список пользователей в группе.
        
        :param group_id: ID группы
        :return: Список пользователей группы
        """
        def _get_users():
            try:
                group = TelegramGroup.objects.get(id=group_id)
                return list(group.users.all())
            except TelegramGroup.DoesNotExist:
                return []
        
        return await AsyncUnitOfWork.execute(_get_users)
    
    async def get_groups_for_user(self, user_id: int) -> List[TelegramGroup]:
        """
        Получает список групп, в которых состоит пользователь.
        
        :param user_id: ID пользователя
        :return: Список групп пользователя
        """
        def _get_groups():
            try:
                user = TelegramUser.objects.get(id=user_id)
                return list(user.groups.all())
            except TelegramUser.DoesNotExist:
                return []
        
        return await AsyncUnitOfWork.execute(_get_groups)
    
    async def create_with_users(self, name: str, description: str = None, user_ids: List[int] = None) -> TelegramGroup:
        """
        Создает новую группу с пользователями.
        
        :param name: Название группы
        :param description: Описание группы
        :param user_ids: Список ID пользователей для добавления в группу
        :return: Созданный объект группы
        """
        def _create_group():
            # Создаем новую группу
            group = TelegramGroup.objects.create(
                name=name,
                description=description
            )
            
            # Если переданы ID пользователей, добавляем их в группу
            if user_ids:
                users = TelegramUser.objects.filter(id__in=user_ids)
                group.users.add(*users)
                
            return group
        
        return await AsyncUnitOfWork.execute(_create_group)