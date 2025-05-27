"""
Обработчики команд и сообщений для Telegram бота
"""

from app.bot.telegram.handlers.start import router as start_router
from app.bot.telegram.handlers.main_menu import router as main_menu_router

__all__ = ["start_router", "main_menu_router"]
