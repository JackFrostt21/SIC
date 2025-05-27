"""
Клавиатуры для процесса регистрации
"""

from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from app.bot.telegram.keyboards.builders import (
    InlineKeyboardBuilder,
    ReplyKeyboardBuilder,
)
from app.organization.models import Company, Department, JobTitle


def get_registration_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для подтверждения регистрации
    """
    buttons = [
        [("✅ Подтвердить", "registration:confirm")],
        [("🔄 Изменить данные", "registration:edit")],
    ]
    return InlineKeyboardBuilder.create_inline_kb(buttons)


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой отправки номера телефона
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


def get_companies_keyboard(companies: List[Company]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора компании

    :param companies: Список компаний
    :return: Клавиатура с компаниями
    """
    buttons = []
    for company in companies:
        buttons.append([(company.name, f"registration:company:{company.id}")])

    return InlineKeyboardBuilder.create_inline_kb(buttons)


def get_departments_keyboard(departments: List[Department]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора департамента

    :param departments: Список департаментов
    :return: Клавиатура с департаментами
    """
    buttons = []
    for department in departments:
        buttons.append([(department.name, f"registration:department:{department.id}")])

    return InlineKeyboardBuilder.create_inline_kb(buttons)


def get_job_titles_keyboard(job_titles: List[JobTitle]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора должности

    :param job_titles: Список должностей
    :return: Клавиатура с должностями
    """
    buttons = []
    for job_title in job_titles:
        buttons.append([(job_title.name, f"registration:job_title:{job_title.id}")])

    return InlineKeyboardBuilder.create_inline_kb(buttons)


def get_registration_edit_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для редактирования данных регистрации
    """
    buttons = [
        [("📱 Телефон", "registration:edit_phone")],
        [("👤 ФИО", "registration:edit_name")],
        [("📧 Email", "registration:edit_email")],
        [("🎂 Дата рождения", "registration:edit_birth_date")],
        [("🏢 Компания", "registration:edit_company")],
        [("🏛️ Департамент", "registration:edit_department")],
        [("👔 Должность", "registration:edit_job_title")],
        [("✅ Готово", "registration:confirm")],
    ]
    return InlineKeyboardBuilder.create_inline_kb(buttons)
