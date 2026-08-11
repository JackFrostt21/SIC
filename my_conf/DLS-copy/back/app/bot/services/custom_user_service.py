from typing import Dict, Any, Optional
from app.bot.repositories.custom_user_repository import CustomUserRepository
from app.bot.models import CustomUser, TelegramUser


class CustomUserService:
    """
    Сервис для работы с кастомными пользователями (веб-аутентификация).
    Содержит бизнес-логику создания пользователей для веб-доступа.
    """

    def __init__(self, custom_user_repository: CustomUserRepository = None):
        self.custom_user_repository = custom_user_repository or CustomUserRepository()

    async def create_from_telegram_user(
        self, telegram_user: TelegramUser, password: str
    ) -> Dict[str, Any]:
        """
        Создает CustomUser на основе данных TelegramUser с паролем для веб-доступа.

        :param telegram_user: Объект TelegramUser для связи
        :param password: Пароль для веб-доступа
        :return: Словарь с результатом операции
        """
        try:
            # TODO: В будущем добавить проверку уникальности email в TelegramUser
            # для предотвращения конфликтов при создании CustomUser

            # Проверяем, не существует ли уже CustomUser для этого TelegramUser
            existing_custom_user = (
                await self.custom_user_repository.get_by_telegram_user_id(
                    telegram_user.id
                )
            )

            if existing_custom_user:
                return {
                    "success": False,
                    "message": "CustomUser уже существует для данного TelegramUser",
                    "custom_user": existing_custom_user,
                }

            # Подготавливаем данные для CustomUser на основе TelegramUser
            custom_user_data = {
                "username": telegram_user.user_name or f"user_{telegram_user.telegram_id}",
                "first_name": telegram_user.first_name or "",
                "last_name": telegram_user.last_name or "",
                "email": telegram_user.email or "",
                "telegram_user": telegram_user,
                "is_active": True,  # Активируем для веб-доступа
            }

            # Создаем CustomUser с хешированным паролем
            custom_user = await self.custom_user_repository.create_with_password(
                password=password, **custom_user_data
            )

            return {
                "success": True,
                "custom_user": custom_user,
                "message": "CustomUser успешно создан",
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при создании CustomUser: {str(e)}",
                "error": str(e),
            }

    async def get_custom_user_by_telegram_id(self, telegram_id: int) -> Dict[str, Any]:
        """
        Получает CustomUser по telegram_id.

        :param telegram_id: ID пользователя в Telegram
        :return: Словарь с результатом операции
        """
        try:
            # Ищем CustomUser через связанный TelegramUser
            custom_user = await self.custom_user_repository.get_by_filter(
                telegram_user__telegram_id=telegram_id
            )

            if custom_user:
                return {"success": True, "custom_user": custom_user}
            else:
                return {"success": False, "message": "CustomUser не найден"}

        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при поиске CustomUser: {str(e)}",
                "error": str(e),
            }

    async def update_password(
        self, custom_user_id: int, new_password: str
    ) -> Dict[str, Any]:
        """
        Обновляет пароль пользователя.

        :param custom_user_id: ID CustomUser
        :param new_password: Новый пароль
        :return: Словарь с результатом операции
        """
        try:
            custom_user = await self.custom_user_repository.get_by_id(custom_user_id)

            if not custom_user:
                return {"success": False, "message": "CustomUser не найден"}

            # Обновляем пароль через встроенный метод Django
            custom_user.set_password(new_password)

            # Сохраняем изменения
            updated_user = await self.custom_user_repository.create_instance(
                custom_user
            )

            return {
                "success": True,
                "custom_user": updated_user,
                "message": "Пароль успешно обновлен",
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при обновлении пароля: {str(e)}",
                "error": str(e),
            }
