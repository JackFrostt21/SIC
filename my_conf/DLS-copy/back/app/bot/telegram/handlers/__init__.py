"""
Обработчики команд и сообщений для Telegram бота
"""

from app.bot.telegram.handlers.registration import router as start_router
from app.bot.telegram.handlers.main_menu import router as main_menu_router
from app.bot.telegram.handlers.testing_handlers import router as testing_router
from app.bot.telegram.handlers.enrollcourse_handlers import (
    router as enrollcourse_router,
)
from app.bot.telegram.handlers.subscription_handlers import (
    router as subscription_router,
)

__all__ = [
    "start_router",
    "main_menu_router",
    "testing_router",
    "enrollcourse_router",
    "subscription_router",
]
