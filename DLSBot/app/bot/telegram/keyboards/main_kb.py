"""
Клавиатура главного меню для Telegram бота
"""

from typing import Optional
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def get_main_menu_keyboard(
    user_id: int, base_url: Optional[str] = None
) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру главного меню

    :param user_id: ID пользователя Telegram
    :param base_url: Базовый URL для веб-приложений (опционально)
    :return: Объект обычной клавиатуры
    """
    # TODO: base_url подумать, оставить или нет?
    # Если базовый URL не указан, используем значение по умолчанию
    if not base_url:
        base_url = "https://educationalbot.engsdrilling.ru"

    # Формируем URL для веб-приложений
    about_bot_url = f"{base_url}/api/testing-testing_module/bot-info/"
    progress_url = f"{base_url}/api/testing-testing_module/progress/?user_id={user_id}"

    # Создаем билдер клавиатуры
    builder = ReplyKeyboardBuilder()

    # Добавляем кнопку программ обучения
    builder.add(KeyboardButton(text="📚 Программы обучения"))

    # Добавляем кнопки с веб-приложениями в одном ряду
    builder.row(
        KeyboardButton(text="📊 Мой прогресс", web_app=WebAppInfo(url=progress_url)),
        KeyboardButton(text="ℹ️ О боте", web_app=WebAppInfo(url=about_bot_url)),
    )

    # Создаем клавиатуру с настройками
    return builder.as_markup(resize_keyboard=True)
