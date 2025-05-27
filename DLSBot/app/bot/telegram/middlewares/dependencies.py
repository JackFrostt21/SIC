"""
Middleware для инъекции зависимостей
"""

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from app.bot.telegram.deps import (
    get_telegram_user_service,
    get_test_service,
    get_course_content_service,
)


class DependencyInjectMiddleware(BaseMiddleware):
    """
    Middleware для инъекции зависимостей в обработчики
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Инъекция сервиса пользователей
        data["user_service"] = get_telegram_user_service()
        data["test_service"] = get_test_service()
        data["course_content_service"] = get_course_content_service()

        # Передаем управление дальше
        return await handler(event, data)
