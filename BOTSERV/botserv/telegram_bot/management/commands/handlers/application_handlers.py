from aiogram import Router, types
from asgiref.sync import sync_to_async
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from telegram_bot.models import DirectoryServices, Applications, TelegramUser, BuildingEriell, FloorEriell, BlockEriell
from .email_handlers import get_user_by_telegram_id


import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


router = Router()

class ApplicationStates(StatesGroup):
    waiting_for_service = State()
    waiting_for_building = State()
    waiting_for_floor = State()
    waiting_for_block = State()
    waiting_for_office_workplace = State()
    waiting_for_internal_number = State()
    waiting_for_manual_internal_number = State() ###111
    waiting_for_mobile_phone = State()
    waiting_for_application_text = State()


@router.message(Command('zayavka'))
async def on_zayavka_command(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user and user.user_eriell is not None:                                   ### убрал  and user.active договорились что без будем работать
        await state.update_data(user_fio=user.user_fio)
        services_list = await sync_to_async(list)(DirectoryServices.objects.all().values_list('name_services', flat=True))
        if services_list:
            builder = InlineKeyboardBuilder()
            for index, service in enumerate(services_list, start=1):
                callback_data = f"service_{index}"
                builder.button(text=service, callback_data=callback_data)
            builder.adjust(1)

            await message.answer("Выберите услугу:", reply_markup=builder.as_markup())
            await state.set_state(ApplicationStates.waiting_for_service)
    else:
        await message.answer("Ваш аккаунт не подтвержден. Пожалуйста, подтвердите ваш email - services.eriell.com.")


@router.callback_query(F.data.startswith("service_"))
async def on_service_selected(callback_query: types.CallbackQuery, state: FSMContext):
    service_index = int(callback_query.data.split('_')[1])  # Получаем индекс выбранной услуги
    services_list = await sync_to_async(list)(DirectoryServices.objects.all().values_list('name_services', flat=True))
    selected_service_name = services_list[service_index - 1]  # Индексы начинаются с 1 в callback_data

    await state.update_data(selected_service_name=selected_service_name)

    await callback_query.message.edit_text(f"Вы выбрали услугу: {selected_service_name}", reply_markup=None)

    buildings_list = await sync_to_async(list)(BuildingEriell.objects.all().values_list('adress_building', flat=True))

    buttons = [InlineKeyboardButton(text=building, callback_data=f'building_{building}') for building in buildings_list]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

    await callback_query.message.answer("Выберите номер здания:", reply_markup=keyboard)

    await state.set_state(ApplicationStates.waiting_for_building)


@router.callback_query(F.data.startswith("building_"))
async def on_building_selected(callback_query: types.CallbackQuery, state: FSMContext):
    building = callback_query.data.split('_')[1]
    await state.update_data(building=building)
    await callback_query.message.edit_text(f"Вы выбрали: {building}", reply_markup=None)

    floors_list = await sync_to_async(list)(FloorEriell.objects.all().values_list('number_floor', flat=True))

    buttons = [[InlineKeyboardButton(text=floor, callback_data=f'floor_{floor}')] for floor in floors_list]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(ApplicationStates.waiting_for_floor)
    await callback_query.message.answer("Выберите номер этажа:", reply_markup=keyboard)
    await callback_query.answer()


@router.callback_query(F.data.startswith("floor_"))
async def on_floor_selected(callback_query: types.CallbackQuery, state: FSMContext):
    floor = callback_query.data.split('_')[1]
    await state.update_data(floor=floor)
    await callback_query.message.edit_text(f"Вы выбрали: {floor}", reply_markup=None)

    blocks_list = await sync_to_async(list)(BlockEriell.objects.all().values_list('number_block', flat=True))

    buttons = [[InlineKeyboardButton(text=block, callback_data=f'block_{block}')] for block in blocks_list]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(ApplicationStates.waiting_for_block)
    await callback_query.message.answer("Выберите номер блока:", reply_markup=keyboard)
    await callback_query.answer()


@router.callback_query(F.data.startswith("block_"))
async def on_block_selected(callback_query: types.CallbackQuery, state: FSMContext):
    block = callback_query.data.split('_')[1]
    await state.update_data(block=block)
    await callback_query.message.edit_text(f"Вы выбрали: {block}", reply_markup=None)

    await state.set_state(ApplicationStates.waiting_for_office_workplace)
    await callback_query.message.answer("Введите кабинет или рабочее место:")
    await callback_query.answer()


@router.message(ApplicationStates.waiting_for_office_workplace)
async def process_office_workplace(message: types.Message, state: FSMContext):
    await state.update_data(office_workplace=message.text)
    
    user = await get_user_by_telegram_id(message.from_user.id)
    if user.internal_number:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"Внутренний номер: {user.internal_number}", callback_data="use_internal_number")],
            [InlineKeyboardButton(text="Ввести другой внутренний номер", callback_data="enter_internal_number_manually")]
        ])
        await message.answer("Выберите действие:", reply_markup=keyboard)
    else:
        await message.answer('Введите ваш внутренний номер телефона:')
        await state.set_state(ApplicationStates.waiting_for_manual_internal_number)


@router.callback_query(F.data == "use_internal_number")
async def use_internal_number(callback_query: types.CallbackQuery, state: FSMContext):
    user = await get_user_by_telegram_id(callback_query.from_user.id)
    # Добавляем внутренний номер и флаг, номер взят из профиля пользователя
    await state.update_data(internal_number=user.internal_number, internal_number_source="profile")
    
    await callback_query.message.edit_text(f"Внутренний номер: {user.internal_number}", reply_markup=None)
    
    if user.mobile_phone:  # Если у пользователя есть мобильный номер
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"Мобильный номер: {user.mobile_phone}", callback_data="use_mobile_phone")],
            [InlineKeyboardButton(text="Ввести другой мобильный номер", callback_data="enter_mobile_phone_manually")]
        ])
        await callback_query.message.answer("Выберите действие для мобильного номера:", reply_markup=keyboard)
        await callback_query.answer()
    else:
        await state.set_state(ApplicationStates.waiting_for_mobile_phone)
        await callback_query.message.answer('Введите номер мобильного телефона:')
        await callback_query.answer()



@router.callback_query(F.data == "enter_internal_number_manually")
async def enter_internal_number_manually(callback_query: types.CallbackQuery, state: FSMContext):
    # Устанавливаем флаг, что пользователь будет вводить номер вручную
    await state.update_data(internal_number_source="manual")
    await state.set_state(ApplicationStates.waiting_for_manual_internal_number)
    
    await callback_query.message.edit_text("Введите ваш внутренний номер телефона в ответном сообщении.", reply_markup=None)
    
    await callback_query.answer()


@router.message(ApplicationStates.waiting_for_manual_internal_number)
async def process_manual_internal_number(message: types.Message, state: FSMContext):
    await state.update_data(internal_number=message.text)
    
    user = await get_user_by_telegram_id(message.from_user.id)
    if user.mobile_phone:  
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"Использовать мобильный номер: {user.mobile_phone}", callback_data="use_mobile_phone")],
            [InlineKeyboardButton(text="Ввести другой мобильный номер", callback_data="enter_mobile_phone_manually")]
        ])
        await message.answer("Выберите действие для мобильного номера:", reply_markup=keyboard)
    else:
        await state.set_state(ApplicationStates.waiting_for_mobile_phone)
        await message.answer('Введите номер мобильного телефона:')

@router.callback_query(F.data == "use_mobile_phone")
async def use_mobile_phone(callback_query: types.CallbackQuery, state: FSMContext):
    user = await get_user_by_telegram_id(callback_query.from_user.id)
    await state.update_data(mobile_phone=user.mobile_phone)
    
    await callback_query.message.edit_text(f"Мобильный номер: {user.mobile_phone}", reply_markup=None)
    await state.set_state(ApplicationStates.waiting_for_application_text)
    await callback_query.message.answer('Введите текст заявки:')
    await callback_query.answer()

@router.callback_query(F.data == "enter_mobile_phone_manually")
async def enter_mobile_phone_manually(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(ApplicationStates.waiting_for_mobile_phone)
    await callback_query.message.edit_text("Введите ваш мобильный номер телефона:", reply_markup=None)
    await callback_query.answer()



@router.message(ApplicationStates.waiting_for_mobile_phone)
async def process_mobile_phone(message: types.Message, state: FSMContext):
    await state.update_data(mobile_phone=message.text)
    await state.set_state(ApplicationStates.waiting_for_application_text)
    await message.answer('Введите текст заявки:')



@router.message(ApplicationStates.waiting_for_application_text)
async def process_application_text(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)                              #Сюда еще подтянуть ФИО 
    await state.update_data(application_text=message.text, user_eriell=user.user_eriell)
    
    data = await state.get_data()

    application_preview = f"Пожалуйста, подтвердите вашу заявку:\n\n" + \
                          f"ФИО: {data.get('user_fio', 'Не указано')}\n" +\
                          f"Здание: {data.get('selected_service_name', 'Не указано')}\n" + \
                          f"Здание: {data.get('building', 'Не указано')}\n" + \
                          f"Этаж: {data.get('floor', 'Не указано')}\n" + \
                          f"Блок: {data.get('block', 'Не указано')}\n" + \
                          f"Офис/Рабочее место: {data.get('office_workplace', 'Не указано')}\n" + \
                          f"Внутренний номер: {data.get('internal_number', 'Не указано')}\n" + \
                          f"Мобильный телефон: {data.get('mobile_phone', 'Не указано')}\n" + \
                          f"Текст заявки: {data.get('application_text', 'Не указано')}"

    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить заявку", callback_data="confirm_application")],
        [InlineKeyboardButton(text="Отменить заявку", callback_data="reject_application")]
    ])

    await message.answer(application_preview, reply_markup=confirm_keyboard)


@router.callback_query(F.data == "confirm_application")
async def confirm_application(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await save_application(data)  # Сохраняем заявку
    await state.clear()  
    await callback_query.message.edit_text("Ваша заявка успешно создана.", reply_markup=None)

@router.callback_query(F.data == "reject_application")
async def reject_application(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()  
    await callback_query.message.edit_text("Заявка отменена.", reply_markup=None)  
    await callback_query.answer()


@sync_to_async
def save_application(data):
    user_fio = data.get('user_fio')
    user_eriell = data.get('user_eriell')
    selected_service_name = data.get('selected_service_name')
    building = data.get('building')
    floor = data.get('floor')
    block = data.get('block')
    office_workplace = data.get('office_workplace')
    internal_number = data.get('internal_number')
    mobile_phone = data.get('mobile_phone')
    application_text = data.get('application_text')

    service = DirectoryServices.objects.filter(name_services=selected_service_name).first()

    Applications.objects.create(
        user_fio=user_fio,
        user_eriell=user_eriell,
        name_services=selected_service_name,
        building=building,
        floor=floor,
        block=block,
        office_workplace=office_workplace,
        internal_number=internal_number,
        mobile_phone=mobile_phone,
        application_text=application_text
    )