"""
Клавиатура для рейтинга курса
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_rating_keyboard(course_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для оценки курса со звездами от 5 до 1
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⭐⭐⭐⭐⭐ (5)", callback_data=f"rating:{course_id}:5")
    keyboard.button(text="⭐⭐⭐⭐ (4)", callback_data=f"rating:{course_id}:4")
    keyboard.button(text="⭐⭐⭐ (3)", callback_data=f"rating:{course_id}:3")
    keyboard.button(text="⭐⭐ (2)", callback_data=f"rating:{course_id}:2")
    keyboard.button(text="⭐ (1)", callback_data=f"rating:{course_id}:1")
    keyboard.adjust(1)
    # Добавляем кнопку "Назад к темам курса"
    keyboard.row(
        InlineKeyboardButton(
            text="🔙 Назад к темам курса", callback_data=f"course:{course_id}"
        )
    )
    return keyboard.as_markup()
