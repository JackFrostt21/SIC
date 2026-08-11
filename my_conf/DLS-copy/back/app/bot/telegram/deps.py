"""
Простые провайдеры сервисов для Telegram бота (без DI контейнера).
"""

from typing import Annotated
from app.bot.services.telegram_user_service import TelegramUserService
from app.bot.services.custom_user_service import CustomUserService
from app.learning_app.services.test_service import TestService
from app.learning_app.services.course_content_service import CourseContentService


# Сервисы для инъекции (например, через middleware в aiogram)
def get_telegram_user_service() -> TelegramUserService:
    return TelegramUserService()


def get_test_service() -> TestService:
    return TestService()


def get_course_content_service() -> CourseContentService:
    return CourseContentService()


def get_custom_user_service() -> CustomUserService:
    return CustomUserService()


# Типы для аннотаций зависимостей
UserService = Annotated[TelegramUserService, get_telegram_user_service]
CustomUserServiceType = Annotated[CustomUserService, get_custom_user_service]
