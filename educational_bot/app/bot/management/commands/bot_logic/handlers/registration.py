from aiogram import types
from aiogram.dispatcher import FSMContext
from asgiref.sync import sync_to_async
import re

from app.bot.management.commands.bot_logic.kb.main_kb import building_main_menu
from app.bot.management.commands.loader import dp
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.bot_logic.functions import user_set_language, load_bot_logo

from app.bot.management.commands.bot_logic.states import LocaleRegSteps
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.models.telegram_user import TelegramUser
from app.educational_module.models import Company

i18n = setup_middleware(dp)
_ = i18n.gettext


def is_email(text):
    try:
        pattern = '^[\w\.\-]+@([\w-]+\.)+[\w-]{2,4}$'
        if re.match(pattern, text):
            return True
        else:
            return False
    except Exception as e:
        print(e)


async def soft_state_finish(state: FSMContext):
    fields = ["action", "Yes_No"]
    data = await state.get_data()
    data = {key: value for key, value in data.items() if key not in fields}
    await state.set_data(data)
    await state.set_state(None)


@sync_to_async
def user_set_info(user_id, full_name, date_of_birth, phone):
    user = TelegramUser.objects.get(user_id=user_id)
    user.state = 1  # допуск пользователя в систему
    user.full_name = full_name
    user.date_of_birth = date_of_birth
    user.phone = phone
    user.save()


"""
Этот обработчик управляет процессом выбора языка пользователем. 
В зависимости от выбора языка, он вызывает функцию user_set_language, 
чтобы сохранить выбранный язык пользователя, и отправляет соответствующее сообщение для ввода имени. 
Затем состояние обновляется на LocaleRegSteps.enter_date_birth.
"""
@dp.message_handler(state=LocaleRegSteps.set_language)
async def set_language(message: types.Message):
    try:
        match message.text:
            case '🇷🇺Русский':
                await user_set_language(message.from_user.id, "ru")
                await message.answer(text='Пожалуйста введите фамилию, имя и отчество через пробел', reply_markup=ReplyKeyboardRemove())

            case "🇺🇿O'zbek":
                await user_set_language(message.from_user.id, "uz")
                await message.answer(text='Iltimos, toʻliq ismingizni kiriting', reply_markup=ReplyKeyboardRemove())
            case '🇬🇧English':
                await user_set_language(message.from_user.id, 'en')
                await message.answer(text='Please share your name', reply_markup=ReplyKeyboardRemove())
        await LocaleRegSteps.enter_date_birth.set()
    except Exception as e:
        print(e)


"""
Этот обработчик обрабатывает ввод имени пользователя. 
Он сохраняет имя в состоянии FSM и отправляет сообщение с запросом даты рождения, 
затем обновляет состояние на LocaleRegSteps.enter_phone.
"""
@dp.message_handler(state=LocaleRegSteps.enter_date_birth)
async def enter_date_birth(message: types.Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await message.answer(text=_('Please enter date_of_birth'), reply_markup=ReplyKeyboardRemove())
        await LocaleRegSteps.enter_phone.set()
    except Exception as e:
        print(e)


"""
Этот обработчик обрабатывает ввод даты рождения. 
Он сохраняет дату рождения в состоянии FSM и отправляет сообщение с запросом на ввод номера телефона, 
предоставляя пользователю клавиатуру для отправки контакта. 
Затем состояние обновляется на LocaleRegSteps.registration_finish.
"""
@dp.message_handler(state=LocaleRegSteps.enter_phone)
async def enter_phone(message: types.Message, state: FSMContext):
    try:
        await state.update_data(birth=message.text)
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton(_('Share contact'), request_contact=True))

        await message.answer(text=_('Please enter share contact'), reply_markup=kb)
        await LocaleRegSteps.registration_finish.set()
    except Exception as e:
        print(e)


"""
Этот обработчик завершает процесс регистрации. 
Он обрабатывает введённые данные, включая контактные данные, 
и сохраняет их в базе данных с помощью функции user_set_info. 
Затем загружает логотип бота, создаёт главное меню и отправляет пользователю фото с сообщением, 
подтверждающим успешную регистрацию. После этого состояние сбрасывается.
"""
@dp.message_handler(content_types=types.ContentType.ANY, state=LocaleRegSteps.registration_finish)
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