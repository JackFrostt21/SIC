from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from ..tg_services.registration_services import (
    is_cyrillic,
    normalize_person_name,
    parse_birth_date,
    is_valid_email,
    upsert_telegram_user,
)
from ..states.registration_state import RegistrationStates

from ..keyboards.registration_kb import (
    get_precheck_keyboard,
    get_phone_keyboard,
    get_company_keyboard,
    # get_departments_keyboard,
    # get_job_titles_keyboard,
    get_email_keyboard,
    get_final_confirm_keyboard,
    get_consent_keyboard,
)
from app.bot.telegram.keyboards.main_kb import get_main_menu_keyboard

from app.bot.telegram.tg_selectors.registration_selectors import (
    check_user_status,
    _get_company_name,
    # _get_department_name,
    # _get_job_title_name,
)
from app.bot.models import TelegramUser
from app.organization.models import Company
from asgiref.sync import sync_to_async
from datetime import datetime
from app.integration.models import RegistrationSetting
from app.integration.services.regbot_client import (
    build_regbot_employee_payload,
    build_regbot_telegram_payload,
    post_regbot,
)
from app.integration.services.onec_mapping import apply_employee_from_onec
from app.bot.telegram.utils.messages import (
    get_consent_request,
    get_consent_declined_message,
    get_password_request,
    get_password_confirmation_request,
    get_invalid_password_message,
    get_password_mismatch_message,
    get_registration_success,
)
from app.bot.telegram.deps import CustomUserServiceType, UserService

router = Router(name="start_router")


@sync_to_async
def _get_registration_settings() -> RegistrationSetting | None:
    return RegistrationSetting.objects.first()


@sync_to_async
def _get_default_company() -> Company | None:
    return Company.objects.filter(is_actual=True).first() or Company.objects.first()


def _extract_employee_from_data(data):
    if isinstance(data, dict):
        return data
    if isinstance(data, list) and data:
        first = data[0]
        return first if isinstance(first, dict) else None
    return None


def _split_fio_text(fio: str | None):
    if not fio:
        return None, None, None

    parts = [part for part in str(fio).strip().split() if part]
    if not parts:
        return None, None, None

    last_name = parts[0] if len(parts) >= 1 else None
    first_name = parts[1] if len(parts) >= 2 else None
    middle_name = " ".join(parts[2:]) if len(parts) >= 3 else None
    return last_name, first_name, middle_name


def _format_birth_date_for_view(raw_value: str | None) -> str | None:
    if not raw_value:
        return None

    try:
        return datetime.strptime(raw_value, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        return raw_value


async def _prepare_found_registration_data(
    *,
    state: FSMContext,
    employee_data,
    source: str,
    telegram_id: int,
    username: str | None,
    last_name: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
) -> bool:
    employee = _extract_employee_from_data(employee_data)
    if not employee:
        return False

    fio_last_name, fio_first_name, fio_middle_name = _split_fio_text(employee.get("fio"))
    resolved_last_name = last_name or fio_last_name
    resolved_first_name = first_name or fio_first_name
    resolved_middle_name = middle_name or fio_middle_name

    await state.update_data(
        found_registration=True,
        found_source=source,
        found_employee=employee,
        telegram_id=telegram_id,
        username=username,
        surname=resolved_last_name,
        name=resolved_first_name,
        patronymic=resolved_middle_name,
        birth_date=_format_birth_date_for_view(employee.get("birthday")),
    )
    return True


async def _start_password_flow_for_found(
    *,
    state: FSMContext,
    employee_data,
    source: str,
    telegram_id: int,
    username: str | None,
    responder,
    last_name: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
) -> bool:
    prepared = await _prepare_found_registration_data(
        state=state,
        employee_data=employee_data,
        source=source,
        telegram_id=telegram_id,
        username=username,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
    )
    if not prepared:
        await responder(
            "Ошибка интеграции. Попробуйте позже.\n"
            "Integratsiya xatosi. Keyinroq urinib ko‘ring"
        )
        return False

    await state.set_state(RegistrationStates.waiting_for_password)
    await responder(get_password_request())
    return True


async def _complete_found_registration(
    *,
    data: dict,
    telegram_id: int,
    password: str,
    custom_user_service: CustomUserServiceType,
    user_service: UserService,
) -> tuple[bool, str | None]:
    if not password:
        return False, "Отсутствует пароль для завершения регистрации"

    employee = _extract_employee_from_data(data.get("found_employee"))
    if not employee:
        return False, "Не удалось получить данные сотрудника из интеграции"

    company = await _get_default_company()
    telegram_user = await sync_to_async(apply_employee_from_onec)(
        employee=employee,
        company=company,
        telegram_id=telegram_id,
        username=data.get("username"),
        last_name=data.get("surname"),
        first_name=data.get("name"),
        middle_name=data.get("patronymic"),
        personal_data_consent=data.get("personal_data_consent"),
    )

    custom_user_result = await custom_user_service.create_from_telegram_user(
        telegram_user=telegram_user,
        password=password,
    )

    if custom_user_result.get("success"):
        await user_service.update_user_status(
            telegram_id=telegram_id,
            status=TelegramUser.STATE_ACTIVE,
        )
        return True, None

    return (
        False,
        "Ошибка создания веб-пользователя: "
        f"{custom_user_result.get('message', 'Неизвестная ошибка')}",
    )


async def _start_manual_registration_flow(responder, state: FSMContext) -> None:
    await responder(
        "Введите вашу фамилию используя только кириллицу. \n"
        "Familiyangizni faqat kirill alifbosida kiriting"
    )
    await state.set_state(RegistrationStates.waiting_for_surname)


async def _continue_registration_after_consent(
    *,
    telegram_id: int,
    username: str | None,
    state: FSMContext,
    responder,
) -> None:
    await state.update_data(telegram_id=telegram_id, username=username)

    # Ищем пользователя локально только по telegram_id
    user_status = await check_user_status(telegram_id)

    if user_status is not None:
        if user_status == TelegramUser.STATE_ACTIVE:
            keyboard = await get_main_menu_keyboard(telegram_id)
            await responder(
                "Для работы с ботом используйте кнопки ниже. \n"
                "Bot bilan ishlash uchun quyidagi tugmalardan foydalaning",
                reply_markup=keyboard,
            )
            await state.clear()
            return

        if user_status == TelegramUser.STATE_NOT_ACTIVE:
            await _start_manual_registration_flow(responder, state)
            return

        if user_status == TelegramUser.STATE_NEED_CONFIRMATION:
            await responder(
                "Ваш аккаунт ожидает подтверждения. Пожалуйста, подождите. \n"
                "Akkauntingiz tasdiqlanmoqda ⏳. Iltimos, kuting"
            )
            await state.clear()
            return

        if user_status == TelegramUser.STATE_DELETED:
            await responder(
                "Ваш аккаунт удалён. Обратитесь в поддержку. \n"
                "Akkauntingiz o‘chirildi ❌. Yordam xizmatiga murojaat qiling"
            )
            await state.clear()
            return

        await _start_manual_registration_flow(responder, state)
        return

    settings = await _get_registration_settings()
    if not settings or not settings.telegram_check_url:
        await responder(
            "Временная ошибка интеграции. Попробуйте позже.\n"
            "Integratsiya vaqtincha ishlamayapti. Keyinroq urinib ko‘ring"
        )
        await state.clear()
        return

    payload = build_regbot_telegram_payload(telegram_id=telegram_id)
    response = await post_regbot(
        url=settings.telegram_check_url,
        payload=payload,
        api_key=settings.api_key,
        timeout_seconds=10.0,
    )

    http_status = response.get("http_status")
    status = response.get("status")

    if http_status == 200 and status == "FOUND":
        await _start_password_flow_for_found(
            state=state,
            employee_data=response.get("data"),
            source="telegram_id",
            telegram_id=telegram_id,
            username=username,
            responder=responder,
        )
        return

    if http_status == 200 and status == "NOT_FOUND":
        await _start_manual_registration_flow(responder, state)
        return

    if http_status == 503 and status == "TEMP_UNAVAILABLE":
        await responder(
            "Временная ошибка интеграции. Попробуйте позже.\n"
            "Integratsiya vaqtincha ishlamayapti. Keyinroq urinib ko‘ring"
        )
        await state.clear()
        return

    await responder(
        "Временная ошибка интеграции. Попробуйте позже.\n"
        "Integratsiya vaqtincha ishlamayapti. Keyinroq urinib ko‘ring"
    )
    await state.clear()


async def _start_manual_registration_from_callback(
    callback: CallbackQuery, state: FSMContext
) -> None:
    keyboard = await get_phone_keyboard()
    await callback.message.answer(
        "Отправьте номер телефона кнопкой ниже.\n"
        "Quyidagi tugma orqali telefon raqamingizni yuboring",
        reply_markup=keyboard,
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    username = message.from_user.username

    await state.update_data(telegram_id=telegram_id, username=username)

    # Сначала проверяем наличие пользователя и его статус локально
    user_status = await check_user_status(telegram_id)

    if user_status == TelegramUser.STATE_ACTIVE:
        keyboard = await get_main_menu_keyboard(telegram_id)
        await message.answer(
            "Для работы с ботом используйте кнопки ниже. \n"
            "Bot bilan ishlash uchun quyidagi tugmalardan foydalaning",
            reply_markup=keyboard,
        )
        await state.clear()
        return

    if user_status == TelegramUser.STATE_NEED_CONFIRMATION:
        await message.answer(
            "Ваш аккаунт ожидает подтверждения. Пожалуйста, подождите. \n"
            "Akkauntingiz tasdiqlanmoqda ⏳. Iltimos, kuting"
        )
        await state.clear()
        return

    if user_status == TelegramUser.STATE_DELETED:
        await message.answer(
            "Ваш аккаунт удалён. Обратитесь в поддержку. \n"
            "Akkauntingiz o‘chirildi ❌. Yordam xizmatiga murojaat qiling"
        )
        await state.clear()
        return

    # Для новых и неактивных пользователей запускаем регистрацию с согласия
    await state.set_state(RegistrationStates.waiting_for_consent)
    await message.answer(
        get_consent_request(),
        reply_markup=await get_consent_keyboard(),
    )



# --------- Согласие ---------
@router.callback_query(
    RegistrationStates.waiting_for_consent,
    F.data.startswith("registration:consent:"),
)
async def process_consent_selection(callback: CallbackQuery, state: FSMContext) -> None:
    action = callback.data.split(":", 2)[2]

    if action == "yes":
        data = await state.get_data()
        telegram_id = data.get("telegram_id") or callback.from_user.id
        username = data.get("username") or callback.from_user.username

        await state.update_data(
            personal_data_consent=True,
            telegram_id=telegram_id,
            username=username,
        )

        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

        await _continue_registration_after_consent(
            telegram_id=telegram_id,
            username=username,
            state=state,
            responder=callback.message.answer,
        )
    else:
        await callback.message.edit_text(
            get_consent_declined_message(), reply_markup=await get_consent_keyboard()
        )

    await callback.answer()



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
    # На этапе pre_ok у нас уже есть ФИО и дата рождения — вызываем RegBot /api/1cchek/
    await callback.message.delete()

    data = await state.get_data()
    last_name = data.get("surname")
    first_name = data.get("name")
    middle_name = data.get("patronymic")
    birth_date_str = data.get("birth_date")  # DD.MM.YYYY
    telegram_id = data.get("telegram_id")
    username = data.get("username")

    # Конвертируем дату из DD.MM.YYYY в YYYY-MM-DD
    try:
        birthday_iso = (
            datetime.strptime(birth_date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            if birth_date_str
            else None
        )
    except Exception:
        birthday_iso = None

    settings = await _get_registration_settings()

    if (
        not settings
        or not settings.employee_check_url
        or not birthday_iso
        or not last_name
        or not first_name
        or not telegram_id
    ):
        await callback.message.answer(
            "Ошибка интеграции. Попробуйте позже.\n"
            "Integratsiya xatosi. Keyinroq urinib ko‘ring"
        )
        return

    payload = build_regbot_employee_payload(
        telegram_id=telegram_id,
        last_name=last_name,
        name=first_name,
        birthday_iso=birthday_iso,
    )
    response = await post_regbot(
        url=settings.employee_check_url,
        payload=payload,
        api_key=settings.api_key,
        timeout_seconds=10.0,
    )

    http_status = response.get("http_status")
    status = response.get("status")

    if http_status == 200 and status == "FOUND":
        await _start_password_flow_for_found(
            state=state,
            employee_data=response.get("data"),
            source="fio_birthday",
            telegram_id=telegram_id,
            username=username,
            responder=callback.message.answer,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
        )
        return

    if http_status == 200 and status == "NOT_FOUND":
        await _start_manual_registration_from_callback(callback, state)
        return

    if http_status == 503 and status == "TEMP_UNAVAILABLE":
        await callback.message.answer("1С не отвечает, попробуйте позже")
        return

    await callback.message.answer(
        "Ошибка интеграции. Попробуйте позже.\n"
        "Integratsiya xatosi. Keyinroq urinib ko‘ring"
    )


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

    keyboard = await get_email_keyboard()
    await callback.message.answer(
        'Введите ваш email или нажмите кнопку "Нет email" \n'
        'Emailingizni kiriting yoki "Нет email" tugmasini bosing',
        reply_markup=keyboard,
    )
    await state.set_state(RegistrationStates.waiting_for_email)
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

    # Переходим к вводу пароля
    await state.set_state(RegistrationStates.waiting_for_password)
    await message.answer(get_password_request())


def validate_password(password: str) -> bool:
    """Валидация пароля"""
    if len(password) < 6:
        return False
    if len(password) > 128:
        return False
    # Добавить дополнительные правила при необходимости
    return True


# --------- Пароль ---------
@router.message(RegistrationStates.waiting_for_password)
async def process_password_input(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод пароля пользователем
    """
    password = message.text.strip()

    # Валидация пароля
    if not validate_password(password):
        await message.answer(get_invalid_password_message())
        return

    # Сохраняем пароль в состояние
    await state.update_data(password=password)

    # Переходим к подтверждению пароля
    await state.set_state(RegistrationStates.waiting_for_password_confirmation)
    await message.answer(get_password_confirmation_request())


# --------- Подтверждение пароля ---------
@router.message(RegistrationStates.waiting_for_password_confirmation)
async def process_password_confirmation(
    message: Message,
    state: FSMContext,
    custom_user_service: CustomUserServiceType,
    user_service: UserService,
) -> None:
    """
    Обрабатывает подтверждение пароля пользователем
    """
    confirmation = message.text.strip()
    user_data = await state.get_data()

    if confirmation != user_data.get("password"):
        await message.answer(get_password_mismatch_message())
        # Возвращаемся к вводу пароля
        await state.set_state(RegistrationStates.waiting_for_password)
        return

    if user_data.get("found_registration"):
        source = user_data.get("found_source")

        if source == "telegram_id":
            registration_success, error_message = await _complete_found_registration(
                data=user_data,
                telegram_id=message.from_user.id,
                password=user_data.get("password"),
                custom_user_service=custom_user_service,
                user_service=user_service,
            )

            if registration_success:
                success_message = get_registration_success()
                main_menu_keyboard = await get_main_menu_keyboard(message.from_user.id)
                await message.answer(success_message, reply_markup=main_menu_keyboard)
            else:
                await message.answer(
                    f"❌ <b>Ошибка завершения регистрации!</b>\n\n"
                    f"Произошла ошибка:\n"
                    f"<i>{error_message or 'Неизвестная ошибка'}</i>"
                )

            await state.clear()
            return

        employee = _extract_employee_from_data(user_data.get("found_employee")) or {}
        fio = employee.get("fio") or "—"
        birthday = _format_birth_date_for_view(employee.get("birthday")) or "—"
        phone = employee.get("phone") or "—"
        email = employee.get("email") or "—"

        overview = (
            "Сотрудник найден. Проверьте данные и подтвердите:\n"
            "Xodim topildi. Ma’lumotlarni tekshirib tasdiqlang:\n\n"
            f"• ФИО / F.I.Sh.: {fio}\n"
            f"• Дата рождения / Tug‘ilgan sana: {birthday}\n"
            f"• Телефон / Telefon: {phone}\n"
            f"• Email: {email}\n"
        )

        await state.set_state(RegistrationStates.waiting_for_final_confirm)
        kb = await get_final_confirm_keyboard()
        await message.answer(overview, reply_markup=kb)
        return

    # Пароли совпадают, переходим к финальному подтверждению
    data = await state.get_data()
    company_name = (
        await _get_company_name(int(data["company"])) if data.get("company") else None
    )

    overview = (
        "Итоги регистрации:\n"
        "Ro‘yxatdan o‘tish natijalari:\n\n"
        f"• Фамилия / Familiya: {data.get('surname')}\n"
        f"• Имя / Ism: {data.get('name')}\n"
        f"• Отчество / Otasining ismi: {data.get('patronymic')}\n"
        f"• Дата рождения / Tug‘ilgan sana: {data.get('birth_date')}\n"
        f"• Телефон / Telefon: {data.get('phone')}\n"
        f"• Компания / Kompaniya: {company_name or data.get('company')}\n"
        f"• Email: {data.get('email') or '—'}\n\n"
        "Проверьте и подтвердите:\n"
        "Tekshirib tasdiqlang:"
    )

    await state.set_state(RegistrationStates.waiting_for_final_confirm)
    kb = await get_final_confirm_keyboard()
    await message.answer(overview, reply_markup=kb)



# Завершаем: сохраняем/обновляем пользователя и создаем CustomUser
@router.callback_query(
    RegistrationStates.waiting_for_final_confirm, F.data == "final_ok"
)
async def final_ok(
    callback: CallbackQuery,
    state: FSMContext,
    custom_user_service: CustomUserServiceType,
    user_service: UserService,
):
    await callback.answer()  # снять крутилку

    data = await state.get_data()
    password = data.get("password")

    telegram_id = callback.from_user.id
    found_registration = bool(data.get("found_registration"))

    registration_success = False
    error_message = None

    if not password:
        error_message = "Отсутствует пароль для завершения регистрации"
    elif found_registration:
        registration_success, error_message = await _complete_found_registration(
            data=data,
            telegram_id=telegram_id,
            password=password,
            custom_user_service=custom_user_service,
            user_service=user_service,
        )
    else:
        # сохраняем пользователя в БД со статусом STATE_NEED_CONFIRMATION
        await upsert_telegram_user(data)

        # Пытаемся получить только что созданного/обновленного пользователя
        user_result = await user_service.user_repository.get_by_telegram_id(telegram_id)

        if user_result:
            # Создаем CustomUser с паролем и связываем с TelegramUser
            custom_user_result = await custom_user_service.create_from_telegram_user(
                telegram_user=user_result,
                password=password,
            )

            if custom_user_result.get("success"):
                # Если CustomUser создан успешно, активируем TelegramUser
                await user_service.update_user_status(
                    telegram_id=telegram_id,
                    status=TelegramUser.STATE_ACTIVE,
                )
                registration_success = True
            else:
                error_message = (
                    "Ошибка создания веб-пользователя: "
                    f"{custom_user_result.get('message', 'Неизвестная ошибка')}"
                )
        else:
            error_message = "Не удалось найти пользователя после сохранения"

    # уберём клавиатуру под итоговым сообщением
    try:
        await callback.message.edit_reply_markup()
    except Exception:
        pass

    if registration_success:
        # Отправляем сообщение об успешной регистрации
        success_message = get_registration_success()

        # Получаем главную клавиатуру
        main_menu_keyboard = await get_main_menu_keyboard(telegram_id)

        # Отправляем сообщение с главной клавиатурой
        await callback.message.answer(success_message, reply_markup=main_menu_keyboard)
    else:
        # Уведомляем пользователя об ошибке и предлагаем попробовать еще раз
        await callback.message.answer(
            f"❌ <b>Ошибка завершения регистрации!</b>\n\n"
            f"Произошла ошибка:\n"
            f"<i>{error_message or 'Неизвестная ошибка'}</i>\n\n"
            f"Ваши данные сохранены, но аккаунт требует подтверждения администратором или повторной попытки."
        )

    await state.clear()



# Пройти заново
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

    data = await state.get_data()
    if data.get("found_registration"):
        await state.set_state(RegistrationStates.waiting_for_password)
        await callback.message.answer(get_password_request())
        return

    kb = await get_phone_keyboard()
    await callback.message.answer(
        "Отправьте номер телефона кнопкой ниже.\n"
        "Quyidagi tugma orqali telefon raqamingizni yuboring",
        reply_markup=kb,
    )
    await state.set_state(RegistrationStates.waiting_for_phone)
