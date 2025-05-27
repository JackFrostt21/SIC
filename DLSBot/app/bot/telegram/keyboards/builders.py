"""
Базовые строители клавиатур для Telegram бота
"""

from typing import List, Tuple, Optional, Union
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


class InlineKeyboardBuilder:
    """
    Строитель для инлайн-клавиатур
    """

    @staticmethod
    def create_inline_kb(
        buttons: List[List[Union[Tuple[str, str], InlineKeyboardButton]]],
    ) -> InlineKeyboardMarkup:
        """
        Создает инлайн-клавиатуру из списка кнопок
        Элементы в row могут быть либо кортежем (текст, callback_data),
        либо уже готовым объектом InlineKeyboardButton.

        :param buttons: Список рядов. Каждый ряд - список кнопок.
        :return: Объект инлайн-клавиатуры
        """
        keyboard = []

        for row_items in buttons:
            keyboard_row = []
            for item in row_items:
                if isinstance(item, InlineKeyboardButton):
                    keyboard_row.append(item)
                elif isinstance(item, tuple) and len(item) == 2:
                    # Убедимся, что оба элемента кортежа - строки (для text и callback_data)
                    text, value = item
                    if isinstance(text, str) and isinstance(value, str):
                        keyboard_row.append(
                            InlineKeyboardButton(text=text, callback_data=value)
                        )
                    else:
                        pass
                else:
                    pass
            if keyboard_row:  # Добавляем ряд, только если в нем есть кнопки
                keyboard.append(keyboard_row)

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def create_inline_kb_with_url(
        buttons: List[List[Tuple[str, str, bool]]],
    ) -> InlineKeyboardMarkup:
        """
        Создает инлайн-клавиатуру с URL-кнопками

        :param buttons: Список списков кнопок в формате (текст, url_или_callback, is_url)
        :return: Объект инлайн-клавиатуры
        """
        keyboard = []

        for row in buttons:
            keyboard_row = []
            for text, value, is_url in row:
                if is_url:
                    keyboard_row.append(InlineKeyboardButton(text=text, url=value))
                else:
                    keyboard_row.append(
                        InlineKeyboardButton(text=text, callback_data=value)
                    )
            keyboard.append(keyboard_row)

        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class ReplyKeyboardBuilder:
    """
    Строитель для обычных клавиатур
    """

    @staticmethod
    def create_reply_kb(
        buttons: List[List[str]],
        resize_keyboard: bool = True,
        one_time_keyboard: bool = False,
    ) -> ReplyKeyboardMarkup:
        """
        Создает обычную клавиатуру из списка кнопок

        :param buttons: Список списков текстов кнопок
        :param resize_keyboard: Подгонять размер клавиатуры под размер экрана
        :param one_time_keyboard: Скрывать клавиатуру после нажатия
        :return: Объект клавиатуры
        """
        keyboard = []

        for row in buttons:
            keyboard_row = []
            for text in row:
                keyboard_row.append(KeyboardButton(text=text))
            keyboard.append(keyboard_row)

        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
        )
