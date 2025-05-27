"""
Зависимости для инъекции в обработчики Telegram бота
"""

from typing import Annotated, Callable, Dict, Any
from aiogram import Bot
from aiogram.types import User as TelegramUserType
from app.bot.services.telegram_user_service import TelegramUserService
from app.learning_app.services.test_service import TestService
from app.learning_app.services.course_content_service import CourseContentService


# Сервисы для инъекции
def get_telegram_user_service() -> TelegramUserService:
    """
    Возвращает экземпляр сервиса для работы с пользователями Telegram
    """
    return TelegramUserService()


def get_test_service() -> TestService:
    """
    Возвращает экземпляр сервиса для управления тестированием.
    """
    return TestService()


def get_course_content_service() -> CourseContentService:
    """
    Возвращает экземпляр сервиса для работы с контентом курсов.
    """
    return CourseContentService()


# Типы для аннотаций зависимостей
UserService = Annotated[TelegramUserService, get_telegram_user_service]
