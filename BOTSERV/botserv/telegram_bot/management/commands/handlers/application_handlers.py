from aiogram import Router, types
from asgiref.sync import sync_to_async
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from telegram_bot.models import DirectoryServices, Applications, TelegramUser
from .email_handlers import get_user_by_telegram_username


import logging

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

router = Router()


class ApplicationStates(StatesGroup):
    waiting_for_building = State()
    waiting_for_floor = State()
    waiting_for_block = State()
    waiting_for_office_workplace = State()
    waiting_for_internal_number = State()
    waiting_for_mobile_phone = State()
    waiting_for_application_text = State()


# async def create_building_buttons(buildings: list) -> InlineKeyboardMarkup:
#     logging.debug(f"Создание кнопок для зданий: {buildings}")
#     print('111')
#     keyboard = InlineKeyboardMarkup() #row_width=3
#     logging.debug(f'KLAVA {keyboard}')
#     print('222')
#     for building in buildings:
#         logging.debug(f"Добавление кнопки для здания: {building}")
#         print('333')
#         button = InlineKeyboardButton(text=building, callback_data=f'building_{building}')
#         print('444')
#         keyboard.add(button)
#         print('555')
#         print(f'тут кнопка {button}')
#     if not keyboard.inline_keyboard:
#         logging.warning("Не добавлено ни одной кнопки в InlineKeyboardMarkup")
#     print(f'тут клавиатура {keyboard}')
#     return keyboard


# async def create_building_buttons(buildings: list) -> InlineKeyboardMarkup:
#     logging.debug(f"Создание кнопок для зданий: {buildings}")
#     buttons = [[InlineKeyboardButton(text=building, callback_data=f'building_{building}') for building in buildings]]
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return keyboard

@router.message(Command('zayavki'))
async def on_zayavki_command(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_username(message.from_user.username)
    if user and user.user_eriell is not None:
        services_list = await sync_to_async(list)(DirectoryServices.objects.all().values_list('name_services', flat=True))
        if services_list:
            builder = InlineKeyboardBuilder()
            for index, service in enumerate(services_list, start=1):
                callback_data = f"service_{index}"
                builder.button(text=service, callback_data=callback_data)
            builder.adjust(1)

            await message.answer("Выберите услугу:", reply_markup=builder.as_markup())
            await state.set_state(ApplicationStates.waiting_for_floor)
        else:
            await message.answer("Услуги не найдены.")
    else:
        await message.answer("Ваш аккаунт не подтвержден. Пожалуйста, подтвердите ваш email - services.eriell.com.")


@router.callback_query(F.data.startswith("service_"))
async def on_service_selected(callback_query: types.CallbackQuery, state: FSMContext):
    name_services = callback_query.data.split('_')[1]
    await state.update_data(name_services=name_services)
    await state.set_state(ApplicationStates.waiting_for_building)
    await callback_query.message.answer("Введите номер здания:")
    await callback_query.answer()



# @router.callback_query(F.data.startswith("service_"))
# async def on_service_selected(callback_query: types.CallbackQuery, state: FSMContext):
#     print('AAA')
#     name_services = callback_query.data.split('_')[1]
#     print('BBB')
#     await state.update_data(name_services=name_services)
#     print('CCC')
#     buildings = ['Здание 1', 'Здание 2', 'Здание 3', 'Здание 4', 'Здание 5', 'Здание 6']
#     print('DDD')
#     logging.debug(f"Вызов create_building_buttons с зданиями: {buildings}")
#     keyboard = await create_building_buttons(buildings)
#     print('EEE')

#     await state.set_state(ApplicationStates.waiting_for_building)
#     print('FFF')
#     await callback_query.message.answer("Выберите номер здания:", reply_markup=keyboard)
#     await callback_query.answer()



@router.message(ApplicationStates.waiting_for_building)
async def process_building(message: types.Message, state: FSMContext):
    await state.update_data(building=message.text)
    await state.set_state(ApplicationStates.waiting_for_floor)
    await message.answer("Введите номер этажа:")


@router.message(ApplicationStates.waiting_for_floor)
async def process_floor(message: types.Message, state: FSMContext):
    await state.update_data(floor=message.text)
    await state.set_state(ApplicationStates.waiting_for_block)
    await message.answer("Введите номер блока:")

@router.message(ApplicationStates.waiting_for_block)
async def process_block(message: types.Message, state: FSMContext):
    await state.update_data(block=message.text)
    await state.set_state(ApplicationStates.waiting_for_office_workplace)
    await message.answer("Введите кабинет или рабочее место:")

@router.message(ApplicationStates.waiting_for_office_workplace)
async def process_office_workplace(message: types.Message, state: FSMContext):
    await state.update_data(office_workplace=message.text)
    await state.set_state(ApplicationStates.waiting_for_internal_number)
    await message.answer('Введите внутренний номер телефона:')

@router.message(ApplicationStates.waiting_for_internal_number)
async def process_internal_number(message: types.Message, state: FSMContext):
    await state.update_data(internal_number=message.text)
    await state.set_state(ApplicationStates.waiting_for_mobile_phone)
    await message.answer('Введите номер мобильного телефона:')

@router.message(ApplicationStates.waiting_for_mobile_phone)
async def process_mobile_phone(message: types.Message, state: FSMContext):
    await state.update_data(mobile_phone=message.text)
    await state.set_state(ApplicationStates.waiting_for_application_text)
    await message.answer('Введите текст заявки:')


@router.message(ApplicationStates.waiting_for_application_text)
async def process_application_text(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_username(message.from_user.username)
    await state.update_data(application_text=message.text, user_eriell=user.user_eriell)
    data = await state.get_data()
    await save_application(data)
    await state.clear()
    await message.answer("Заявка создана.")


@sync_to_async
def save_application(data):
    user_eriell = data.get('user_eriell')
    name_services = data.get('name_services')
    building = data.get('building')
    floor = data.get('floor')
    block = data.get('block')
    office_workplace = data.get('office_workplace')
    internal_number = data.get('internal_number')
    mobile_phone = data.get('mobile_phone')
    application_text = data.get('application_text')
    
   
    service = DirectoryServices.objects.filter(id=name_services).first()
    name_services = service.name_services if service else None


    Applications.objects.create(
        user_eriell=user_eriell,
        name_services=name_services,
        building=building,
        floor=floor,
        block=block,
        office_workplace=office_workplace,
        internal_number=internal_number,
        mobile_phone=mobile_phone,
        application_text=application_text
    )


@router.message(Command('spisok'))
async def on_spisok_command(message: types.Message):
    telegram_username = message.from_user.username

    try:
        user = await sync_to_async(TelegramUser.objects.get)(username_telegram=telegram_username)
        user_applications_qs = await sync_to_async(Applications.objects.filter)(user_eriell=user.user_eriell)
    except TelegramUser.DoesNotExist:
        await message.answer("Пользователь не найден.")
        return

    # Преобразуем queryset в список асинхронно
    user_applications = await sync_to_async(list)(user_applications_qs)

    if not user_applications:
        await message.answer("Заявки не найдены.")
        return

    for application in user_applications:
        application_info = (
            f"Услуга: {application.name_services}\n"
            f"Здание: {application.building}\n"
            f"Этаж: {application.floor}\n"
            f"Блок: {application.block}\n"
            f"Офис/Рабочее место: {application.office_workplace}\n"
            f"Внутренний номер: {application.internal_number}\n"
            f"Мобильный телефон: {application.mobile_phone}\n"
            f"Текст заявки: {application.application_text}"
        )
        await message.answer(application_info)

