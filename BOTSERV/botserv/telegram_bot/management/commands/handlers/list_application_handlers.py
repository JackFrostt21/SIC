from aiogram import Router, types
from asgiref.sync import sync_to_async
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F

from telegram_bot.models import Applications, TelegramUser
from typing import Union

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


router = Router()

PAGE_SIZE = 1


async def show_page(message_or_query: Union[types.Message, types.CallbackQuery], page: int, is_callback: bool = False):
    telegram_id = message_or_query.from_user.id

    try:
        user = await sync_to_async(TelegramUser.objects.get)(number_user_telegram=telegram_id)
        user_applications_qs = await sync_to_async(Applications.objects.filter)(user_eriell=user.user_eriell)
    except TelegramUser.DoesNotExist:
        response_text = "Пользователь не найден."
        if is_callback:
            await message_or_query.message.answer(response_text)
        else:
            await message_or_query.answer(response_text)
        return

    total_applications = await sync_to_async(user_applications_qs.count)()
    if total_applications == 0:
        response_text = "Заявки не найдены."
        if is_callback:
            await message_or_query.message.answer(response_text)
        else:
            await message_or_query.answer(response_text)
        return

    # Определение индексов для текущей страницы
    start_index = page * PAGE_SIZE
    end_index = start_index + PAGE_SIZE

    # Получение заявок для текущей страницы
    user_applications = await sync_to_async(list)(user_applications_qs[start_index:end_index])

    for application in user_applications:
        application_info = (
            f"Услуга: {application.name_services}, Статус: в работе\n\n"
            f"Место работы: {application.building}, {application.floor}, {application.block}, Кабинет: {application.office_workplace}\n\n"
            f"Текст заявки: {application.application_text}"
        )
        pagination_keyboard = get_pagination_keyboard(page, total_applications)
        if is_callback:
            await message_or_query.message.edit_text(application_info, reply_markup=pagination_keyboard)
        else:
            await message_or_query.answer(application_info, reply_markup=pagination_keyboard)
        break  # Добавляем break, чтобы отправить информацию только о первой заявке в списке



def get_pagination_keyboard(current_page: int, total_items: int) -> InlineKeyboardMarkup:
    total_pages = -(-total_items // PAGE_SIZE)  # Округление вверх

    buttons = []
    # Кнопка "Предыдущая" (если не первая страница)
    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=f"page_{current_page - 1}"))
    # Кнопка "Следующая" (если не последняя страница)
    if current_page + 1 < total_pages:
        buttons.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=f"page_{current_page + 1}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard


@router.message(Command('spisok'))
async def on_spisok_command(message: types.Message):
    await show_page(message, page=0)


@router.callback_query(F.data.startswith("page_"))
async def on_page_callback(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[1])
    await show_page(callback_query, page, is_callback=True)
    await callback_query.answer()