"""
Клавиатура для управления подписками на уведомления о новых курсах
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.bot.telegram.callback.schemas import SubscriptionCallback


async def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для управления подписками

    :return: Объект инлайн-клавиатуры с кнопками включения/отключения уведомлений
    """
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки для управления подписками
    builder.button(
        text="✅ Включить уведомления",
        callback_data=SubscriptionCallback(action="enable").pack(),
    )
    builder.button(
        text="🔕 Отключить уведомления",
        callback_data=SubscriptionCallback(action="disable").pack(),
    )

    # Выстраиваем по 1 кнопке в ряду
    builder.adjust(1)

    return builder.as_markup()
