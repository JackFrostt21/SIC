from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    KeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    CallbackQuery,
)
from asgiref.sync import sync_to_async
from icecream import ic

from typing import (
    Union,
)

from app.bot.management.commands.bot_logic.functions import (
    user_exists,
    load_bot_logo,
    user_change_test_status,
)
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.bot_logic.states import LocaleRegSteps
from app.bot.management.commands.loader import dp

from app.bot.models.telegram_user import UserAction, TelegramUser
from app.bot.management.commands.bot_logic.kb.main_kb import building_main_menu

i18n = setup_middleware(dp)
_ = i18n.gettext


@sync_to_async
def get_telegram_user(user_id):
    try:
        return TelegramUser.objects.get(user_id=user_id)
    except TelegramUser.DoesNotExist:
        return None

async def show_main_menu(message: types.Message):
    user = await get_telegram_user(message.from_user.id)

    if not user:
        await message.answer("Пользователь не найден в базе данных.")
        return

    # Используем данные из модели вместо данных из message.from_user
    first_name = user.first_name if user.first_name else "Имя не указано"
    middle_name = user.middle_name if user.middle_name else " "

    # Логотип и меню
    title, content, photo = await load_bot_logo("main_menu_logo", message.from_user.id)
    menu_keyboard = await building_main_menu(message.from_user.id)
    media = types.InputFile(photo)


    await message.answer_photo(
        photo=media,
        caption=f'{title},\n'
                f'<b>{first_name} {middle_name}</b>\n', 
        reply_markup=menu_keyboard,
    )


@dp.message_handler(commands=["start"], state="*")
async def cmd_start(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    try:
        user_status = await user_exists(
            message.from_user.id, message.from_user.full_name, message.from_user.mention
        )
        
        match user_status:
            case TelegramUser.STATE_ACTIVE:
                await show_main_menu(message)

            case TelegramUser.STATE_NOT_ACTIVE:
                title, content, photo = await load_bot_logo(
                    "welcome_logo", message.from_user.id
                )
                media = types.InputFile(photo)
                await message.answer_photo(
                    photo=media,
                    caption=f"Добро пожаловать,\n"
                            f"в систему дистанционного обучения!\n\n"
                            f"Пожалуйста, выберите язык:\n",
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton("🇷🇺Русский"),
                                KeyboardButton("🇺🇿O'zbek"),
                                KeyboardButton("🇬🇧English"),
                            ]
                        ],
                        resize_keyboard=True,
                    ),
                )
                await LocaleRegSteps.set_language.set()

            case TelegramUser.STATE_DELETED:
                await message.answer(
                    text=_("Ваша учетная запись Заблокирована. Для получения дополнительной информации свяжитесь с администратором центра обучения."),
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton("/start")]], resize_keyboard=True
                    ),
                )

    except Exception as e:
        print(e)


from . import callbackhandlers

ic(callbackhandlers)


@dp.callback_query_handler(text_contains="btn_done")
async def settings_set_done(call: CallbackQuery):
    try:
        await call.message.delete_reply_markup()
        await call.message.delete()
        match await user_exists(
            call.from_user.id, call.from_user.full_name, call.from_user.mention
        ):
            case 1:
                title, content, photo = await load_bot_logo(
                    "main_menu_logo", call.from_user.id
                )
                menu_keyboard = await building_main_menu(call.from_user.id)
                media = types.InputFile(photo)
                await call.message.answer_photo(
                    photo=media,
                    caption=f"<code>{title}\n"
                    f"{content}\n</code>"
                    f"<i>{call.from_user.full_name}</i>\n"
                    f" <b>{call.from_user.mention}</b>",
                    reply_markup=menu_keyboard,
                )
            case 0:
                title, content, photo = await load_bot_logo(
                    "welcome_logo", call.from_user.id
                )
                media = types.InputFile(photo)
                await call.message.answer_photo(
                    photo=media,
                    caption=f"<code>{title}\n"
                    f"{content}\n</code>"
                    f"<i>{call.from_user.full_name}</i>\n"
                    f" <b>{call.from_user.mention}</b>",
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton("🇷🇺Русский"),
                                KeyboardButton("🇺🇿O'zbek"),
                                KeyboardButton("🇬🇧English"),
                            ]
                        ],
                        resize_keyboard=True,
                    ),
                )
                await LocaleRegSteps.set_language.set()
            case 2:
                title, content, photo = await load_bot_logo(
                    "user_blocked_logo", call.from_user.id
                )
                content = _(
                    "The module will be available after the Administrator checks."
                )
                media = types.InputFile(photo)
                await call.message.answer_photo(
                    photo=media,
                    caption=f"<code>{title}\n"
                    f"{content}\n</code>"
                    f"<i>{call.from_user.full_name}</i>\n"
                    f" <b>{call.from_user.mention}</b>",
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton("/start")]], resize_keyboard=True
                    ),
                )
    except Exception as e:
        print(e)


@dp.callback_query_handler(state="*")
async def any_callback(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(InlineKeyboardMarkup())