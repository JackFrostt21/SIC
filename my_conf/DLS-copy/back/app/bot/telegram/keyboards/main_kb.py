"""
Клавиатура главного меню для Telegram бота
"""

from typing import Optional
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.organization.repositories import SettingsBotRepository


async def get_main_menu_keyboard(
    user_id: int, base_url: Optional[str] = None
) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру главного меню

    :param user_id: ID пользователя Telegram
    :param base_url: Базовый URL для веб-приложений (опционально)
    :return: Объект обычной клавиатуры
    """
    # Если базовый URL не указан, пробуем взять из SettingsBot
    if not base_url:
        settings_repo = SettingsBotRepository()
        base_url = await settings_repo.get_url_web_app()
        if not base_url:
            base_url = "https://learning.engsdrilling.ru"

    # Формируем URL для веб-приложений
    # Нормализуем слеши
    base_url = base_url.rstrip("/")

    about_bot_url = f"{base_url}/webapp/bot-info/?user_id={user_id}"
    progress_url = f"{base_url}/webapp/progress/?user_id={user_id}"

    # Создаем билдер клавиатуры
    builder = ReplyKeyboardBuilder()

    # Добавляем кнопку программ обучения
    builder.row(
        KeyboardButton(text="📚 Программы обучения"),
        KeyboardButton(text="✏️ Самозапись на курсы"),
    )

    # Добавляем кнопку управления уведомлениями
    builder.row(KeyboardButton(text="🔔 Уведомления о новых курсах"))

    # Добавляем кнопки с веб-приложениями в одном ряду
    builder.row(
        KeyboardButton(text="📊 Мой прогресс", web_app=WebAppInfo(url=progress_url)),
        KeyboardButton(text="ℹ️ О боте", web_app=WebAppInfo(url=about_bot_url)),
    )

    # Создаем клавиатуру с настройками
    return builder.as_markup(resize_keyboard=True)
