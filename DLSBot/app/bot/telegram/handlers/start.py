"""
Обработчик команды /start и процесса регистрации
"""

import os
from typing import Dict, Any, List, Optional
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
import logging

from app.bot.telegram.deps import UserService
from app.bot.telegram.states.registration import RegistrationStates
from app.bot.telegram.keyboards.registration import (
    get_registration_confirmation_keyboard,
    get_phone_keyboard,
    get_companies_keyboard,
    get_departments_keyboard,
    get_job_titles_keyboard,
    get_registration_edit_keyboard,
)
from app.bot.telegram.keyboards.main_kb import get_main_menu_keyboard
from app.bot.telegram.utils.messages import (
    get_welcome_message,
    get_registration_name_request,
    get_registration_phone_request,
    get_registration_email_request,
    get_registration_birth_date_request,
    get_registration_company_request,
    get_registration_department_request,
    get_registration_job_title_request,
    get_registration_confirmation,
    get_registration_success,
)
from app.organization.repositories import (
    CompanyRepository,
    DepartmentRepository,
    JobTitleRepository,
    SettingsBotRepository,
)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Создаем роутер для команды /start и процесса регистрации
router = Router(name="start_router")

# Инициализируем репозитории
company_repo = CompanyRepository()
department_repo = DepartmentRepository()
job_title_repo = JobTitleRepository()
settings_repo = SettingsBotRepository()


# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(
    message: Message, state: FSMContext, user_service: UserService
) -> None:
    """
    Обработчик команды /start
    Начинает процесс регистрации пользователя или показывает главное меню
    """
    logger.info(f"Entering cmd_start handler")
    # Получаем информацию о пользователе из Telegram
    telegram_id = message.from_user.id
    username = message.from_user.username

    # Проверяем, существует ли пользователь в системе
    result = await user_service.register_user(
        telegram_id=telegram_id, username=username, full_name=None
    )

    # Логируем результат для отладки
    print(f"User registration result: {result}")
    if result.get("user"):
        print(f"User state: {result['user'].state}")

    # Если пользователь уже активен, показываем главное меню
    if result.get("user") and result["user"].state == 1:  # STATE_ACTIVE
        # Получаем главную клавиатуру
        from app.bot.telegram.keyboards.main_kb import get_main_menu_keyboard

        main_menu_keyboard = await get_main_menu_keyboard(telegram_id)

        # Получаем стартовое изображение
        start_image_path = await settings_repo.get_start_image_path()

        # Отправляем приветственное сообщение с изображением и клавиатурой
        if start_image_path and os.path.exists(start_image_path):
            photo = FSInputFile(start_image_path)
            await message.answer_photo(
                photo=photo,
                caption="<b>👋 С возвращением!</b>\n\n"
                "Выберите раздел для продолжения работы с ботом:",
                reply_markup=main_menu_keyboard,
            )
        else:
            await message.answer(
                "<b>👋 С возвращением!</b>\n\n"
                "Выберите раздел для продолжения работы с ботом:",
                reply_markup=main_menu_keyboard,
            )
        return

    # Получаем стартовое изображение
    start_image_path = await settings_repo.get_start_image_path()

    # Отправляем приветственное сообщение с изображением, если оно есть
    if start_image_path and os.path.exists(start_image_path):
        photo = FSInputFile(start_image_path)
        await message.answer_photo(
            photo=photo, caption=get_welcome_message(is_new_user=result["is_new"])
        )
    else:
        await message.answer(get_welcome_message(is_new_user=result["is_new"]))

    # Начинаем процесс регистрации с запроса телефона
    await state.set_state(RegistrationStates.waiting_for_phone)
    await message.answer(
        get_registration_phone_request(), reply_markup=get_phone_keyboard()
    )


# Обработчик ввода телефона текстом
@router.message(RegistrationStates.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод телефона пользователем в виде текста
    """
    # Сохраняем телефон в контексте
    await state.update_data(phone=message.text)

    # Переходим к выбору компании
    await state.set_state(RegistrationStates.waiting_for_company)
    # Получаем список компаний из репозитория
    companies = await company_repo.get_all_companies()
    await message.answer(
        get_registration_company_request(),
        reply_markup=get_companies_keyboard(companies),
    )


# Обработчик получения контакта
@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает получение контакта от пользователя
    """
    # Сохраняем телефон из контакта
    await state.update_data(phone=message.contact.phone_number)

    # Переходим к выбору компании
    await state.set_state(RegistrationStates.waiting_for_company)
    # Получаем список компаний из репозитория
    companies = await company_repo.get_all_companies()
    await message.answer(
        get_registration_company_request(),
        reply_markup=get_companies_keyboard(companies),
    )


# Обработчик выбора компании
@router.callback_query(
    RegistrationStates.waiting_for_company, F.data.startswith("registration:company:")
)
async def process_company_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает выбор компании
    """
    # Получаем ID компании из callback_data
    company_id = int(callback.data.split(":", 2)[2])

    # Сохраняем ID компании в контексте
    await state.update_data(company_id=company_id)

    # Переходим к выбору департамента
    await state.set_state(RegistrationStates.waiting_for_department)

    # Получаем список департаментов для выбранной компании
    departments = await department_repo.get_departments_by_company(company_id)

    await callback.message.edit_text(
        get_registration_department_request(),
        reply_markup=get_departments_keyboard(departments),
    )

    await callback.answer()


# Обработчик выбора департамента
@router.callback_query(
    RegistrationStates.waiting_for_department,
    F.data.startswith("registration:department:"),
)
async def process_department_selection(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Обрабатывает выбор департамента
    """
    # Получаем ID департамента из callback_data
    department_id = int(callback.data.split(":", 2)[2])

    # Сохраняем ID департамента в контексте
    await state.update_data(department_id=department_id)

    # Переходим к выбору должности
    await state.set_state(RegistrationStates.waiting_for_job_title)

    # Получаем список должностей для выбранного департамента
    job_titles = await job_title_repo.get_job_titles_by_department(department_id)

    # Если должностей нет, получаем все должности
    if not job_titles:
        job_titles = await job_title_repo.get_all_job_titles()

    await callback.message.edit_text(
        get_registration_job_title_request(),
        reply_markup=get_job_titles_keyboard(job_titles),
    )

    await callback.answer()


# Обработчик выбора должности
@router.callback_query(
    RegistrationStates.waiting_for_job_title,
    F.data.startswith("registration:job_title:"),
)
async def process_job_title_selection(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Обрабатывает выбор должности
    """
    # Получаем ID должности из callback_data
    job_title_id = int(callback.data.split(":", 2)[2])

    # Сохраняем ID должности в контексте
    await state.update_data(job_title_id=job_title_id)

    # Переходим к вводу ФИО
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await callback.message.edit_text(get_registration_name_request())

    await callback.answer()


# Обработчик ввода ФИО
@router.message(RegistrationStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод ФИО пользователем
    """
    # Сохраняем ФИО в контексте
    await state.update_data(full_name=message.text)

    # Переходим к вводу email
    await state.set_state(RegistrationStates.waiting_for_email)
    await message.answer(get_registration_email_request())


# Обработчик ввода email
@router.message(RegistrationStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод email пользователем
    """
    # Сохраняем email в контексте
    await state.update_data(email=message.text)

    # Переходим к вводу даты рождения
    await state.set_state(RegistrationStates.waiting_for_birth_date)
    await message.answer(get_registration_birth_date_request())


# Обработчик ввода даты рождения
@router.message(RegistrationStates.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод даты рождения пользователем
    """
    # Сохраняем дату рождения в контексте
    await state.update_data(date_of_birth=message.text)

    # Переходим к подтверждению данных
    await state.set_state(RegistrationStates.waiting_for_confirmation)

    # Получаем все данные из контекста
    user_data = await state.get_data()

    # Формируем сообщение с подтверждением
    confirmation_message = await get_registration_confirmation(user_data)

    await message.answer(
        confirmation_message,
        reply_markup=get_registration_confirmation_keyboard(),
    )


# Обработчик колбэков регистрации
@router.callback_query(F.data.startswith("registration:"))
async def process_registration_callback(
    callback: CallbackQuery, state: FSMContext, user_service: UserService
) -> None:
    """
    Обрабатывает колбэки в процессе регистрации
    """
    # Получаем действие из callback_data
    action = callback.data.split(":", 1)[1]

    # Если это выбор компании, департамента или должности, пропускаем
    if (
        action.startswith("company:")
        or action.startswith("department:")
        or action.startswith("job_title:")
    ):
        return

    # Получаем текущее состояние и данные
    current_state = await state.get_state()
    user_data = await state.get_data()

    if action == "confirm":
        # Подтверждение регистрации
        telegram_id = callback.from_user.id
        username = callback.from_user.username

        # Обновляем данные пользователя
        result = await user_service.register_user(
            telegram_id=telegram_id, username=username, **user_data
        )

        # Активируем пользователя
        await user_service.update_user_status(
            telegram_id=telegram_id, status=1  # STATE_ACTIVE
        )

        # Очищаем состояние
        await state.clear()

        # Отправляем сообщение об успешной регистрации
        success_message = get_registration_success()

        # Получаем главную клавиатуру
        main_menu_keyboard = await get_main_menu_keyboard(telegram_id)

        # Отправляем сообщение с главной клавиатурой
        await callback.message.answer(success_message, reply_markup=main_menu_keyboard)

    elif action == "edit":
        confirmation_message = await get_registration_confirmation(user_data)
        await callback.message.edit_text(
            confirmation_message,
            reply_markup=get_registration_edit_keyboard(),
        )

    elif action.startswith("edit_"):
        field = action.split("_")[1]

        if field == "phone":
            await state.set_state(RegistrationStates.waiting_for_phone)
            await callback.message.edit_text(get_registration_phone_request())
            await callback.message.answer(
                get_registration_phone_request(), reply_markup=get_phone_keyboard()
            )

        elif field == "name":
            await state.set_state(RegistrationStates.waiting_for_full_name)
            await callback.message.edit_text(get_registration_name_request())

        elif field == "email":
            await state.set_state(RegistrationStates.waiting_for_email)
            await callback.message.edit_text(get_registration_email_request())

        elif field == "birth_date":
            await state.set_state(RegistrationStates.waiting_for_birth_date)
            await callback.message.edit_text(get_registration_birth_date_request())

        elif field == "company":
            await state.set_state(RegistrationStates.waiting_for_company)
            companies = await company_repo.get_all_companies()
            await callback.message.edit_text(
                get_registration_company_request(),
                reply_markup=get_companies_keyboard(companies),
            )

        elif field == "department":
            company_id = user_data.get("company_id")
            if company_id:
                await state.set_state(RegistrationStates.waiting_for_department)
                departments = await department_repo.get_departments_by_company(
                    company_id
                )
                await callback.message.edit_text(
                    get_registration_department_request(),
                    reply_markup=get_departments_keyboard(departments),
                )
            else:
                # Если компания не выбрана, сначала выбираем компанию
                await state.set_state(RegistrationStates.waiting_for_company)
                companies = await company_repo.get_all_companies()
                await callback.message.edit_text(
                    get_registration_company_request(),
                    reply_markup=get_companies_keyboard(companies),
                )

        elif field == "job_title":
            department_id = user_data.get("department_id")
            if department_id:
                await state.set_state(RegistrationStates.waiting_for_job_title)
                job_titles = await job_title_repo.get_job_titles_by_department(
                    department_id
                )
                if not job_titles:
                    job_titles = await job_title_repo.get_all_job_titles()
                await callback.message.edit_text(
                    get_registration_job_title_request(),
                    reply_markup=get_job_titles_keyboard(job_titles),
                )
            else:
                # Если департамент не выбран, сначала выбираем департамент
                company_id = user_data.get("company_id")
                if company_id:
                    await state.set_state(RegistrationStates.waiting_for_department)
                    departments = await department_repo.get_departments_by_company(
                        company_id
                    )
                    await callback.message.edit_text(
                        get_registration_department_request(),
                        reply_markup=get_departments_keyboard(departments),
                    )
                else:
                    # Если компания не выбрана, сначала выбираем компанию
                    await state.set_state(RegistrationStates.waiting_for_company)
                    companies = await company_repo.get_all_companies()
                    await callback.message.edit_text(
                        get_registration_company_request(),
                        reply_markup=get_companies_keyboard(companies),
                    )

    await callback.answer()
