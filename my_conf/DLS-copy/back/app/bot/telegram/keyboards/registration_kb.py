from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


from app.bot.telegram.tg_selectors.registration_selectors import (
    get_company_only_list,
    get_department_only_list,
    get_job_title_only_list,
)


async def get_precheck_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Подтвердить / Tasdiqlash", callback_data="pre_ok")
    keyboard.button(
        text="❌ Указать заново / Qaytadan kiritish", callback_data="pre_retry"
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def get_phone_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Отправить номер телефона / Telefon raqamingizni yuborish",
                    request_contact=True,
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


async def get_company_keyboard() -> InlineKeyboardMarkup:
    companies = await get_company_only_list()
    keyboard = InlineKeyboardBuilder()
    for company in companies:
        keyboard.button(text=company.name, callback_data=f"company_{company.id}")
    keyboard.adjust(1)
    return keyboard.as_markup()


# Убрал департаменты и должности - много элементов
# async def get_departments_keyboard(company_id: int) -> InlineKeyboardMarkup:
#     departments = await get_department_only_list(company_id)
#     keyboard = InlineKeyboardBuilder()
#     for department in departments:
#         keyboard.button(text=department.name, callback_data=f'department_{department.id}')
#     keyboard.adjust(1)
#     return keyboard.as_markup()


# async def get_job_titles_keyboard(department_id: int) -> InlineKeyboardMarkup:
#     job_titles = await get_job_title_only_list(department_id)
#     keyboard = InlineKeyboardBuilder()
#     for job_title in job_titles:
#         keyboard.button(text=job_title.name, callback_data=f'job_title_{job_title.id}')
#     keyboard.adjust(1)
#     return keyboard.as_markup()


async def get_email_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Нет email")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


async def get_final_confirm_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="✅ Завершить регистрацию / Ro‘yxatdan o‘tishni yakunlash",
        callback_data="final_ok",
    )
    kb.button(
        text="↩️ Ввести данные заново / Ma’lumotlarni qayta kiritish",
        callback_data="final_retry",
    )
    kb.adjust(1)
    return kb.as_markup()


async def get_consent_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Согласен / Roziman", callback_data="registration:consent:yes"
    )
    keyboard.button(
        text="❌ Отказаться / Rad etish", callback_data="registration:consent:no"
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
