from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from ..services.registration_services import (
    is_cyrillic,
    normalize_person_name,
    parse_birth_date,
    is_valid_email,
    upsert_telegram_user,
)
from ..states import RegistrationStates
from ..keyboards.registration_kb import (
    get_precheck_keyboard,
    get_phone_keyboard,
    get_company_keyboard,
    # get_departments_keyboard,
    # get_job_titles_keyboard,
    get_email_keyboard,
    get_final_confirm_keyboard,
)
from app.bot.telegram.keyboards.lightning_kb import get_lightning_main_menu_kb
from app.bot.telegram.selectors.registration_selectors import (
    check_user_status,
    _get_company_name,
    # _get_department_name,
    # _get_job_title_name,
)
from app.bot.models import TelegramUser
from asgiref.sync import sync_to_async
from datetime import datetime
from app.integration.models import APISettings
from app.integration.services.onec_client import build_onec_payload, post_onec
from app.integration.services.onec_mapping import apply_employee_from_onec

router = Router(name="start_router")


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    # Забираем id и username пользователя
    telegram_id = message.from_user.id
    username = message.from_user.username

    await state.update_data(telegram_id=telegram_id, username=username)

    # Проверяем, есть ли пользователь в базе данных
    user_status = await check_user_status(telegram_id)

    keyboard = get_lightning_main_menu_kb()

    if user_status == TelegramUser.STATE_ACTIVE:
        await message.answer(
            "Для работы с ботом используйте кнопки ниже. \n"
            "Bot bilan ishlash uchun quyidagi tugmalardan foydalaning",
            reply_markup=keyboard,
        )
    elif user_status == TelegramUser.STATE_NOT_ACTIVE or user_status is None:
        await message.answer(
            "Введите вашу фамилию используя только кириллицу. \n"
            "Familiyangizni faqat kirill alifbosida kiriting"
        )
        await state.set_state(RegistrationStates.waiting_for_surname)
    elif user_status == TelegramUser.STATE_NEED_CONFIRMATION:
        await message.answer(
            "Ваш аккаунт ожидает подтверждения. Пожалуйста, подождите. \n"
            "Akkauntingiz tasdiqlanmoqda ⏳. Iltimos, kuting"
        )
    elif user_status == TelegramUser.STATE_DELETED:
        await message.answer(
            "Ваш аккаунт удалён. Обратитесь в поддержку. \n"
            "Akkauntingiz o‘chirildi ❌. Yordam xizmatiga murojaat qiling"
        )


# --------- Фамилия ---------
@router.message(RegistrationStates.waiting_for_surname)
async def surname_handler(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    if not is_cyrillic(raw):
        await message.answer(
            "Введена некорректная фамилия. Фамилия должна быть написана только кириллицей.\n"
            "Familiyangizni faqat kirill alifbosida kiriting"
        )
        return
    surname = normalize_person_name(raw)
    await state.update_data(surname=surname)

    await message.answer(
        "Введите ваше имя используя только кириллицу.\n"
        "Ismingizni faqat kirill alifbosida kiriting"
    )
    await state.set_state(RegistrationStates.waiting_for_name)


# --------- Имя ---------
@router.message(RegistrationStates.waiting_for_name)
async def name_handler(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    if not is_cyrillic(raw):
        await message.answer(
            "Введено некорректное имя. Имя должно быть написано только кириллицей.\n"
            "Ismingizni faqat kirill alifbosida kiriting"
        )
        return
    name = normalize_person_name(raw)
    await state.update_data(name=name)

    await message.answer(
        "Введите ваше отчество используя только кириллицу.\n"
        "Otasiningizni faqat kirill alifbosida kiriting"
    )
    await state.set_state(RegistrationStates.waiting_for_patronymic)


# --------- Отчество ---------
@router.message(RegistrationStates.waiting_for_patronymic)
async def patronymic_handler(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    if not is_cyrillic(raw):
        await message.answer(
            "Введено некорректное отчество. Отчество должно быть написано только кириллицей.\n"
            "Otasiningizni faqat kirill alifbosida kiriting"
        )
        return
    patronymic = normalize_person_name(raw)
    await state.update_data(patronymic=patronymic)

    await message.answer(
        "Введите дату рождения в формате ДДММГГГГ (например: 01012000).\n"
        "Tug‘ilgan kuningizni DDMMYYYY formatida kiriting (masalan: 01012000)"
    )
    await state.set_state(RegistrationStates.waiting_for_birth_date)


# --------- Дата рождения ---------
@router.message(RegistrationStates.waiting_for_birth_date)
async def birth_date_handler(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    d = parse_birth_date(raw)
    if not d:
        await message.answer(
            "Введена некорректная дата рождения. Введите строго 8 цифр: ДДММГГГГ, пример 01012000.\n"
            "Siz noto‘g‘ri tug‘ilgan sana kiritildi. Faqat 8 ta raqam kiriting: DDMMYYYY, masalan 01012000"
        )
        return

    dob_str = d.strftime("%d.%m.%Y")
    await state.update_data(birth_date=dob_str)

    data = await state.get_data()
    text = (
        "Проверьте данные:\n"
        "Ma’lumotlarni tekshiring:\n\n"
        f"• Фамилия / Familiya: {data.get('surname')}\n"
        f"• Имя / Ism: {data.get('name')}\n"
        f"• Отчество / Otasining ismi: {data.get('patronymic')}\n"
        f"• Дата рождения / Tug‘ilgan sana: {dob_str}"
    )

    keyboard = await get_precheck_keyboard()
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_precheck)


@router.callback_query(RegistrationStates.waiting_for_precheck, F.data == "pre_ok")
async def precheck_ok(callback: CallbackQuery, state: FSMContext):
    # На этапе pre_ok у нас уже есть ФИО и дата рождения — вызываем 1С
    # await callback.answer("Смотрим в 1С…")
    await callback.message.delete()

    data = await state.get_data()
    last_name = data.get("surname")
    first_name = data.get("name")
    middle_name = data.get("patronymic")
    birth_date_str = data.get("birth_date")  # DD.MM.YYYY

    # Конвертируем дату из DD.MM.YYYY в YYYY-MM-DD для запроса и хранения
    try:
        birthday_iso = (
            datetime.strptime(birth_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            if birth_date_str
            else None
        )
    except Exception:
        birthday_iso = None

    # Получаем настройки API (первую запись APISettings)
    get_settings = APISettings.objects.select_related("company").first
    settings = await sync_to_async(get_settings)()

    # Если нет настроек/обязательных данных — переходим в ручную регистрацию (телефон)
    if (
        not settings
        or not settings.api_url
        or not settings.api_username
        or not settings.api_password
        or not birthday_iso
        or not last_name
        or not first_name
    ):
        keyboard = await get_phone_keyboard()
        await callback.message.answer(
            "Отправьте номер телефона кнопкой ниже.\n"
            "Quyidagi tugma orqali telefon raqamingizni yuboring",
            reply_markup=keyboard,
        )
        await state.set_state(RegistrationStates.waiting_for_phone)
        return

    payload = build_onec_payload(
        last_name=last_name, name=first_name, birthday_iso=birthday_iso
    )
    response = await post_onec(
        url=settings.api_url,
        username=settings.api_username,
        password=settings.api_password,
        payload=payload,
        timeout_seconds=10.0,
    )

    records = (response or {}).get("data") if isinstance(response, dict) else None
    if records and isinstance(records, list):
        employee = records[0]
        # Применяем данные и завершаем регистрацию как Active
        telegram_id = data.get("telegram_id")
        username = data.get("username")
        await sync_to_async(apply_employee_from_onec)(
            employee=employee,
            company=settings.company,
            telegram_id=telegram_id,
            username=username,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
        )

        keyboard = get_lightning_main_menu_kb()
        await callback.message.answer(
            "Данные найдены в 1С и профиль обновлён.\n"
            "Используйте меню ниже для продолжения работы.\n\n"
            "Ma’lumotlar 1C dan topildi va profil yangilandi.\n"
            "Davom etish uchun quyidagi menyudan foydalaning.",
            reply_markup=keyboard,
        )
        # Очищаем состояние, регистрация завершена
        await state.clear()
        return

    # Иначе продолжаем ручную регистрацию (как было)
    keyboard = await get_phone_keyboard()
    await callback.message.answer(
        "Отправьте номер телефона кнопкой ниже.\n"
        "Quyidagi tugma orqali telefon raqamingizni yuboring",
        reply_markup=keyboard,
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.callback_query(RegistrationStates.waiting_for_precheck, F.data == "pre_retry")
async def precheck_retry(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await callback.message.edit_text(
        "Введите вашу фамилию используя только кириллицу.\n"
        "Familiyangizni faqat kirill alifbosida kiriting"
    )
    await state.set_state(RegistrationStates.waiting_for_surname)


# --------- Телефон ---------
@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def phone_handler(message: Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer(
            "Пожалуйста, отправьте свой собственный номер телефона.\n"
            "Iltimos, o‘z telefon raqamingizni yuboring."
        )
        return

    phone = message.contact.phone_number
    await state.update_data(phone=phone)

    await message.answer(
        "Спасибо, номер получен ✅\nRahmat, raqam qabul qilindi ✅",
        reply_markup=ReplyKeyboardRemove(),
    )

    keyboard = await get_company_keyboard()
    await message.answer(
        "Выберите компанию из списка.\nTashkilotlardan birini tanlang",
        reply_markup=keyboard,
    )
    await state.set_state(RegistrationStates.waiting_for_company)


@router.message(RegistrationStates.waiting_for_phone)
async def phone_wrong_handler(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, используйте кнопку ниже для отправки номера телефона.\n"
        "Quyidagi tugma orqali telefon raqamingizni yuboring",
        reply_markup=await get_phone_keyboard(),
    )


# --------- Компания ---------
@router.callback_query(
    RegistrationStates.waiting_for_company, F.data.startswith("company_")
)
async def company_handler(callback: CallbackQuery, state: FSMContext):
    company_id = callback.data.removeprefix("company_")
    await state.update_data(company=company_id)

    # keyboard = await get_departments_keyboard(company_id)
    # await callback.message.edit_text(
    #     "Выберите департамент из списка.\nDepartmanlardan birini tanlang",
    #     reply_markup=keyboard,
    # )
    # await state.set_state(RegistrationStates.waiting_for_department)


# # --------- Департамент ---------
# @router.callback_query(
#     RegistrationStates.waiting_for_department, F.data.startswith("department_")
# )
# async def department_handler(callback: CallbackQuery, state: FSMContext):
#     department_id = callback.data.removeprefix("department_")
#     await state.update_data(department=department_id)

#     keyboard = await get_job_titles_keyboard(department_id)
#     await callback.message.edit_text(
#         "Выберите должность из списка.\nLavozimlardan birini tanlang",
#         reply_markup=keyboard,
#     )
#     await state.set_state(RegistrationStates.waiting_for_job_title)


# # --------- Должность ---------
# @router.callback_query(
#     RegistrationStates.waiting_for_job_title, F.data.startswith("job_title_")
# )
# async def job_title_handler(callback: CallbackQuery, state: FSMContext):
#     job_title_id = callback.data.removeprefix("job_title_")
#     await state.update_data(job_title=job_title_id)

    keyboard = await get_email_keyboard()
    await callback.message.answer(
        'Введите ваш email или нажмите кнопку "Нет email" \n'
        'Emailingizni kiriting yoki "Нет email" tugmasini bosing',
        reply_markup=keyboard,
    )
    await state.set_state(RegistrationStates.waiting_for_email)
    # тушим кнопку с должностью, потом посмотреть чего она подвисает
    await callback.answer()


# --------- Email ---------
@router.message(RegistrationStates.waiting_for_email)
async def email_handler(message: Message, state: FSMContext):
    raw = (message.text or "").strip()

    if raw.lower() == "нет email":
        await state.update_data(email=None)
        await message.answer(
            "Email пропущен. ✅\nEmail o‘tkazib yuborildi. ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif is_valid_email(raw):
        await state.update_data(email=raw)
        await message.answer(
            "Email сохранён. ✅\nEmail saqlandi. ✅", reply_markup=ReplyKeyboardRemove()
        )
    else:
        keyboard = await get_email_keyboard()
        await message.answer(
            'Введён некорректный email. Укажите корректный адрес или нажмите "Нет email".\n'
            'Emailingiz noto‘g‘ri. To‘g‘ri manzil kiriting yoki "Нет email" tugmasini bosing.',
            reply_markup=keyboard,
        )
        return

    data = await state.get_data()
    company_name = (
        await _get_company_name(int(data["company"])) if data.get("company") else None
    )
    # department_name = (
    #     await _get_department_name(int(data["department"]))
    #     if data.get("department")
    #     else None
    # )
    # job_title_name = (
    #     await _get_job_title_name(int(data["job_title"]))
    #     if data.get("job_title")
    #     else None
    # )

    overview = (
        "Итоги регистрации:\n"
        "Ro‘yxatdan o‘tish natijalari:\n\n"
        f"• Фамилия / Familiya: {data.get('surname')}\n"
        f"• Имя / Ism: {data.get('name')}\n"
        f"• Отчество / Otasining ismi: {data.get('patronymic')}\n"
        f"• Дата рождения / Tug‘ilgan sana: {data.get('birth_date')}\n"
        f"• Телефон / Telefon: {data.get('phone')}\n"
        f"• Компания / Kompaniya: {company_name or data.get('company')}\n"
        # f"• Департамент / Bo‘lim: {department_name or data.get('department')}\n"
        # f"• Должность / Lavozim: {job_title_name or data.get('job_title')}\n"
        f"• Email: {data.get('email') or '—'}\n\n"
        "Проверьте и подтвердите:\n"
        "Tekshirib tasdiqlang:"
    )

    await state.set_state(RegistrationStates.waiting_for_final_confirm)
    kb = await get_final_confirm_keyboard()
    await message.answer(overview, reply_markup=kb)


# Завершаем: сохраняем/обновляем пользователя и ставим NEED_CONFIRMATION
@router.callback_query(
    RegistrationStates.waiting_for_final_confirm, F.data == "final_ok"
)
async def final_ok(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # снять крутилку

    data = await state.get_data()
    # сохраняем пользователя в БД со статусом STATE_NEED_CONFIRMATION
    await upsert_telegram_user(data)

    # уберём клавиатуру под итоговым сообщением, чтобы не сломать логику
    try:
        await callback.message.edit_reply_markup()
    except Exception:
        pass

    await callback.message.answer(
        "Заявка отправлена на подтверждение ✅\n" "Ariza tasdiqlashga yuborildi ✅\n\n"
    )
    await state.set_state(RegistrationStates.waiting_for_confirmation)


# Пройти заново: возвращаем к шагу с телефоном
@router.callback_query(
    RegistrationStates.waiting_for_final_confirm, F.data == "final_retry"
)
async def final_retry(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    # уберём клавиатуру под итоговым сообщением, чтобы не сломать логику
    try:
        await callback.message.edit_reply_markup()
    except Exception:
        pass

    kb = await get_phone_keyboard()
    await callback.message.answer(
        "Отправьте номер телефона кнопкой ниже.\n"
        "Quyidagi tugma orqali telefon raqamingizni yuboring",
        reply_markup=kb,
    )
    await state.set_state(RegistrationStates.waiting_for_phone)
