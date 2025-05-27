"""
Функции для формирования сообщений бота
"""

from typing import Dict, Any, Optional
from app.bot.models import TelegramUser
from app.organization.models import Company, Department, JobTitle, SettingsBot
from asgiref.sync import sync_to_async
from app.organization.repositories import (
    CompanyRepository,
    DepartmentRepository,
    JobTitleRepository,
)


def get_welcome_message(is_new_user: bool = True) -> str:
    """
    Возвращает приветственное сообщение

    :param is_new_user: Флаг нового пользователя
    :return: HTML-форматированное сообщение
    """
    if is_new_user:
        return (
            "<b>👋 Добро пожаловать в образовательную платформу!</b>\n\n"
            "Для начала работы необходимо пройти регистрацию.\n"
            "Пожалуйста, следуйте инструкциям."
        )
    else:
        return (
            "<b>👋 С возвращением!</b>\n\n"
            "Рады видеть вас снова в нашей образовательной платформе."
        )


def get_registration_phone_request() -> str:
    """
    Возвращает сообщение с запросом телефона

    :return: HTML-форматированное сообщение
    """
    return (
        "<b>📱 Введите ваш номер телефона</b>\n\n"
        "Пожалуйста, введите номер телефона в любом формате\n"
        "или нажмите на кнопку ниже для отправки контакта."
    )


def get_registration_name_request() -> str:
    """
    Возвращает сообщение с запросом ФИО

    :return: HTML-форматированное сообщение
    """
    return (
        "<b>👤 Введите ваше ФИО</b>\n\n"
        "Пожалуйста, введите ваше полное имя в формате:\n"
        "<i>Фамилия Имя Отчество</i>"
    )


def get_registration_email_request() -> str:
    """
    Возвращает сообщение с запросом email

    :return: HTML-форматированное сообщение
    """
    return (
        "<b>📧 Введите ваш email</b>\n\n"
        "Пожалуйста, введите ваш действующий email адрес."
    )


def get_registration_birth_date_request() -> str:
    """
    Возвращает сообщение с запросом даты рождения

    :return: HTML-форматированное сообщение
    """
    return (
        "<b>🎂 Введите вашу дату рождения</b>\n\n"
        "Пожалуйста, введите дату рождения в формате ДД.ММ.ГГГГ\n"
        "Например: 01.01.1990"
    )


def get_registration_company_request() -> str:
    """
    Возвращает сообщение с запросом выбора компании

    :return: HTML-форматированное сообщение
    """
    return (
        "<b>🏢 Выберите вашу компанию</b>\n\n"
        "Пожалуйста, выберите компанию из списка ниже:"
    )


def get_registration_department_request() -> str:
    """
    Возвращает сообщение с запросом выбора департамента

    :return: HTML-форматированное сообщение
    """
    return (
        "<b>🏛️ Выберите ваш департамент</b>\n\n"
        "Пожалуйста, выберите департамент из списка ниже:"
    )


def get_registration_job_title_request() -> str:
    """
    Возвращает сообщение с запросом выбора должности

    :return: HTML-форматированное сообщение
    """
    return (
        "<b>👔 Выберите вашу должность</b>\n\n"
        "Пожалуйста, выберите должность из списка ниже:"
    )


async def get_entity_names(user_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Асинхронно получает названия компании, департамента и должности

    :param user_data: Данные пользователя
    :return: Словарь с названиями
    """
    company_name = "Не указано"
    department_name = "Не указано"
    job_title_name = "Не указано"

    # Инициализируем репозитории
    company_repo = CompanyRepository()
    department_repo = DepartmentRepository()
    job_title_repo = JobTitleRepository()

    # Получаем названия компании, департамента и должности
    try:
        if user_data.get("company_id"):
            company_name = await company_repo.get_company_name(
                user_data.get("company_id")
            )

        if user_data.get("department_id"):
            department_name = await department_repo.get_department_name(
                user_data.get("department_id")
            )

        if user_data.get("job_title_id"):
            job_title_name = await job_title_repo.get_job_title_name(
                user_data.get("job_title_id")
            )
    except Exception:
        pass

    return {
        "company_name": company_name,
        "department_name": department_name,
        "job_title_name": job_title_name,
    }


async def get_registration_confirmation(user_data: Dict[str, Any]) -> str:
    """
    Возвращает сообщение с подтверждением регистрации

    :param user_data: Данные пользователя
    :return: HTML-форматированное сообщение
    """
    # Получаем названия компании, департамента и должности
    entity_names = await get_entity_names(user_data)

    return (
        "<b>✅ Проверьте введенные данные:</b>\n\n"
        f"<b>Телефон:</b> {user_data.get('phone', 'Не указано')}\n"
        f"<b>Компания:</b> {entity_names['company_name']}\n"
        f"<b>Департамент:</b> {entity_names['department_name']}\n"
        f"<b>Должность:</b> {entity_names['job_title_name']}\n\n"
        f"<b>ФИО:</b> {user_data.get('full_name', 'Не указано')}\n"
        f"<b>Email:</b> {user_data.get('email', 'Не указано')}\n"
        f"<b>Дата рождения:</b> {user_data.get('date_of_birth', 'Не указано')}\n"
        "Если данные верны, нажмите <b>Подтвердить</b>.\n"
        "Если нужно внести изменения, нажмите <b>Изменить данные</b>."
    )


def get_registration_success() -> str:
    """
    Возвращает сообщение об успешной регистрации

    :return: HTML-форматированное сообщение
    """
    return (
        "<b>🎉 Регистрация успешно завершена!</b>\n\n"
        "Теперь вы можете приступить к обучению.\n"
        "Используйте кнопки ниже для навигации по боту:"
    )


def get_user_profile(user_info: Dict[str, Any]) -> str:
    """
    Возвращает сообщение с профилем пользователя

    :param user_info: Информация о пользователе
    :return: HTML-форматированное сообщение
    """
    return (
        "<b>👤 Ваш профиль:</b>\n\n"
        f"<b>ID:</b> {user_info.get('id')}\n"
        f"<b>ФИО:</b> {user_info.get('full_name', 'Не указано')}\n"
        f"<b>Телефон:</b> {user_info.get('phone', 'Не указано')}\n"
        f"<b>Email:</b> {user_info.get('email', 'Не указано')}\n"
        f"<b>Дата рождения:</b> {user_info.get('date_of_birth', 'Не указано')}\n"
        f"<b>Компания:</b> {user_info.get('company', 'Не указано')}\n"
        f"<b>Отдел:</b> {user_info.get('department', 'Не указано')}\n"
        f"<b>Должность:</b> {user_info.get('job_title', 'Не указано')}\n"
        f"<b>Статус:</b> {user_info.get('status', 'Не указано')}"
    )
