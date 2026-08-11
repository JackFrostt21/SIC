from typing import Optional
from app.core.async_utils import AsyncRepository
from app.bot.models import CustomUser


class CustomUserRepository(AsyncRepository[CustomUser]):
    """
    Репозиторий для работы с кастомными пользователями (веб-аутентификация).
    Предоставляет асинхронные методы для основных операций с моделью CustomUser.
    """

    def __init__(self):
        super().__init__(CustomUser)

    async def get_by_email(self, email: str) -> Optional[CustomUser]:
        """
        Получает пользователя по email.

        :param email: Email пользователя
        :return: Объект пользователя или None, если пользователь не найден
        """
        return await self.get_by_filter(email=email)

    async def get_by_username(self, username: str) -> Optional[CustomUser]:
        """
        Получает пользователя по username.

        :param username: Username пользователя
        :return: Объект пользователя или None, если пользователь не найден
        """
        return await self.get_by_filter(username=username)

    async def get_by_telegram_user_id(
        self, telegram_user_id: int
    ) -> Optional[CustomUser]:
        """
        Получает CustomUser по ID связанного TelegramUser.

        :param telegram_user_id: ID связанного TelegramUser
        :return: Объект пользователя или None, если пользователь не найден
        """
        return await self.get_by_filter(telegram_user_id=telegram_user_id)

    async def create_with_password(self, password: str, **user_data) -> CustomUser:
        """
        Создает пользователя с хешированным паролем.

        :param password: Пароль в открытом виде
        :param user_data: Остальные данные пользователя
        :return: Созданный объект CustomUser
        """
        # Создаем пользователя без сохранения
        user = CustomUser(**user_data)

        # Хешируем пароль через встроенный метод Django
        user.set_password(password)

        # Сохраняем пользователя асинхронно
        return await self.create_instance(user)

    async def create_instance(self, user_instance: CustomUser) -> CustomUser:
        """
        Сохраняет уже созданный экземпляр CustomUser.

        :param user_instance: Экземпляр CustomUser для сохранения
        :return: Сохраненный объект CustomUser
        """
        from app.core.async_utils import AsyncUnitOfWork

        def _save_user():
            user_instance.save()
            return user_instance

        return await AsyncUnitOfWork.execute(_save_user)
