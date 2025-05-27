from aiogram import types
from aiogram.dispatcher import FSMContext
from asgiref.sync import sync_to_async
import re

from app.bot.management.commands.bot_logic.kb.main_kb import building_main_menu
# from app.bot.management.commands.bot_logic.kb.lightning_kb import building_main_menu_lightning
from app.bot.management.commands.loader import dp
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.bot_logic.functions import user_set_language, load_bot_logo

from app.bot.management.commands.bot_logic.states import LocaleRegSteps
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.models.telegram_user import TelegramUser, TelegramGroup
from app.educational_module.models import Company
from app.reference_data.models import JobTitle, Department


i18n = setup_middleware(dp)
_ = i18n.gettext


async def soft_state_finish(state: FSMContext):
    fields = ["action", "Yes_No"]
    data = await state.get_data()
    data = {key: value for key, value in data.items() if key not in fields}
    await state.set_data(data)
    await state.set_state(None)


@sync_to_async
def get_job_titles():
    titles = JobTitle.objects.all()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [KeyboardButton(title.title) for title in titles]
    keyboard.add(*buttons)
    return keyboard


@sync_to_async
def get_departments():
    departments = Department.objects.all()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [KeyboardButton(department.title) for department in departments]
    keyboard.add(*buttons)
    return keyboard


@sync_to_async
def user_set_info(user_id, full_name, date_of_birth, phone, job_title=None, department=None):
    user = TelegramUser.objects.get(user_id=user_id)
    user.state = 1
    user.full_name = full_name
    user.date_of_birth = date_of_birth
    user.phone = phone
    # if job_title:
    #     user.job_title = JobTitle.objects.get(title=job_title)
    # if department:
    #     user.department = Department.objects.get(title=department)
    user.save()

    # group = TelegramGroup.objects.filter(lightning_group=True).order_by('id').first()
    # if group:
    #     group.users.add(user)
    #     group.save()    


@dp.message_handler(state=LocaleRegSteps.set_language)
async def set_language(message: types.Message):
    try:
        match message.text:
            case '🇷🇺Русский':
                await user_set_language(message.from_user.id, "ru")
                await message.answer(text='Пожалуйста введите фамилию, имя и отчество через пробел', reply_markup=ReplyKeyboardRemove())
            # case "🇺🇿O'zbek":
            #     await user_set_language(message.from_user.id, "uz")
            #     await message.answer(text='Iltimos, toʻliq ismingizni kiriting', reply_markup=ReplyKeyboardRemove())
            # case '🇬🇧English':
            #     await user_set_language(message.from_user.id, 'en')
            #     await message.answer(text='Please share your full name', reply_markup=ReplyKeyboardRemove())
        await LocaleRegSteps.enter_full_name.set()
    except Exception as e:
        print(e)


# @dp.message_handler(state=LocaleRegSteps.enter_full_name)
# async def enter_full_name(message: types.Message, state: FSMContext):
#     try:
#         await state.update_data(name=message.text)
#         await message.answer(text='Пожалуйста выберите должность', reply_markup=await get_job_titles())
#         await LocaleRegSteps.enter_job_title.set()
#     except Exception as e:
#         print(e)


# @dp.message_handler(state=LocaleRegSteps.enter_job_title)
# async def select_job_title(message: types.Message, state: FSMContext):
#     try:
#         await state.update_data(job_title=message.text)
#         await message.answer(text='Пожалуйста выберите подразделение', reply_markup=await get_departments())
#         await LocaleRegSteps.enter_department.set()
#     except Exception as e:
#         print(e)


@dp.message_handler(state=LocaleRegSteps.enter_full_name)
async def select_department(message: types.Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await message.answer(text='Пожалуйста введите вашу дату рождения в формате ДД.ММ.ГГГГ', reply_markup=ReplyKeyboardRemove())
        await LocaleRegSteps.enter_date_birth.set()
    except Exception as e:
        print(e)


@dp.message_handler(state=LocaleRegSteps.enter_date_birth)
async def enter_date_birth(message: types.Message, state: FSMContext):
    try:
        await state.update_data(birth=message.text)
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton(_('Share contact'), request_contact=True))
        await message.answer(text='Пожалуйста введите ваш телефонный номер в формате +71112223344', reply_markup=kb)
        await LocaleRegSteps.enter_phone.set()
    except Exception as e:
        print(e)


@dp.message_handler(content_types=types.ContentType.ANY, state=LocaleRegSteps.enter_phone)
async def registration_finish(message: types.Message, state: FSMContext):
    try:
        if message.contact:
            await state.update_data(phone=message.contact.phone_number)
        if message.text:
            await state.update_data(phone=message.text)
        data = await state.get_data()
        enter_full_name = data.get('name')
        date_birth = data.get('birth')
        phone = data.get('phone')
        # job_title = data.get('job_title')
        # department = data.get('department')
        
        # await user_set_info(message.from_user.id, enter_full_name, date_birth, phone, job_title, department)
        await user_set_info(message.from_user.id, enter_full_name, date_birth, phone)
        
        title, content, photo = await load_bot_logo('welcome_logo', message.from_user.id)
        menu_keyboard = await building_main_menu(message.from_user.id)
        media = types.InputFile(photo)
        await message.answer_photo(photo=media,
                                   caption=f'{title}\n'
                                           f'{content}'
                                           f'<i>{message.from_user.full_name}</i>'
                                           f' <code>{message.from_user.mention}</code>',
                                   reply_markup=menu_keyboard)
        await soft_state_finish(state)

    except Exception as e:
        print(e)