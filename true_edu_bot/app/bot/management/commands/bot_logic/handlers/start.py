from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    KeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    CallbackQuery,
)
import aiohttp
from django.db import IntegrityError
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

from app.bot.models.telegram_user import UserAction, TelegramUser, TelegramGroup
from app.bot.management.commands.bot_logic.kb.main_kb import building_main_menu
from app.educational_module.models import RegistrationSetting
# from app.bot.management.commands.bot_logic.kb.lightning_kb import building_main_menu_lightning

i18n = setup_middleware(dp)
_ = i18n.gettext

# @sync_to_async
# def is_user_in_lightning_group(user_id):
#     return TelegramGroup.objects.filter(lightning_group=True, users__id=user_id).exists()

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

    menu_keyboard = await building_main_menu(user.id)

    # Логотип и меню
    title, content, photo = await load_bot_logo("main_menu_logo", message.from_user.id)
    media = types.InputFile(photo)

    first_name = user.first_name if user.first_name else "Имя не указано"
    middle_name = user.middle_name if user.middle_name else " "

    await message.answer_photo(
        photo=media,
        caption=f'{title},\n'
                f'<b>{first_name} {middle_name}</b>\n', 
        reply_markup=menu_keyboard,
    )


@sync_to_async
def update_user_info_in_edubot(telegram_id, regbot_data: dict):
    try:
        # Ищем пользователя по telegram_id
        user = TelegramUser.objects.get(user_id=telegram_id)
        
        user.user_name = regbot_data.get("telegram_user_name") or user.user_name
        user.tg_mention = regbot_data.get("telegram_user_name") or user.tg_mention

        user.save()
        return True
    except TelegramUser.DoesNotExist:
        return False
    except IntegrityError as ie:
        print(f"Ошибка сохранения данных: {ie}")
        return False



# @dp.message_handler(commands=["start"], state="*")
# async def cmd_start(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
#     try:
#         # Сначала проверяем, есть ли пользователь в EDUBot и получаем его статус:
#         user_status = await user_exists(
#             message.from_user.id, 
#             message.from_user.full_name, 
#             message.from_user.mention
#         )

#         match user_status:
#             case TelegramUser.STATE_ACTIVE:
#                 # Если пользователь уже "активен" в EDUBot, показываем основное меню.
#                 await show_main_menu(message)

#             case TelegramUser.STATE_NOT_ACTIVE:
#                 # Загружаем настройки регистрации (синглтон)
#                 reg_settings = await sync_to_async(RegistrationSetting.get_solo)()
#                 # Если regbot_work=True, значит нужно стучаться в RegBot
#                 if reg_settings.regbot_work:
#                     regbot_user_url = f"{reg_settings.url_regbot}{message.from_user.id}"
#                     print(f"Обращаемся к RegBot по URL: {regbot_user_url}")

#                     async with aiohttp.ClientSession() as session:
#                         try:
#                             async with session.get(regbot_user_url) as resp:
#                                 print(f"Получен статус ответа: {resp.status}")
                                
#                                 # Печатаем текст ответа для отладки
#                                 response_text = await resp.text()
#                                 print(f"Текст ответа: {response_text}")

#                                 if resp.status == 200:
#                                     # Пользователь найден в RegBot
#                                     regbot_data = await resp.json()
#                                     print(f"Полученные данные из RegBot: {regbot_data}")

#                                     # Обновляем данные от RegBot (ПРОВЕРИТЬ!!!)
#                                     await update_user_info_in_edubot(message.from_user.id, regbot_data)
#                                     # После обновления данных отдаем функционал курсов
#                                     await show_main_menu(message)
#                                 elif resp.status == 404:
#                                     # Пользователь в RegBot не найден – отправляем ссылку на бота
#                                     await message.answer(
#                                         text=(
#                                             "Вы ещё не зарегистрированы в корпоративном RegBot.\n"
#                                             f"Пожалуйста, пройдите регистрацию по ссылке:\n{reg_settings.bot_reg_url}"
#                                         )
#                                     )
#                                 else:
#                                     # Если вернулся статус, отличный от 200 или 404,
#                                     # считаем это ошибкой обращения к API
#                                     await message.answer(
#                                         text="Ошибка при обращении к сервису регистрации. Попробуйте позже."
#                                     )
#                         except Exception as api_exc:
#                             # Если случилась сетевая ошибка, таймаут и т.п.
#                             print(f"RegBot API error: {api_exc}")
#                             await message.answer(
#                                 text="Ошибка сети при обращении к RegBot. Попробуйте позже."
#                             )
#                 else:
#                     title, content, photo = await load_bot_logo("welcome_logo", message.from_user.id)
#                     media = types.InputFile(photo)
#                     await message.answer_photo(
#                         photo=media,
#                         caption=(
#                             f"Добро пожаловать,\n"
#                             f"в корпоративный бот!\n\n"
#                             f"Пожалуйста, выберите язык:\n"
#                         ),
#                         reply_markup=types.ReplyKeyboardMarkup(
#                             keyboard=[[KeyboardButton("🇷🇺Русский")]],
#                             resize_keyboard=True,
#                         ),
#                     )
#                     await LocaleRegSteps.set_language.set()

#             case TelegramUser.STATE_DELETED:
#                 await message.answer(
#                     text=_("Ваша учетная запись заблокирована. Для получения дополнительной информации свяжитесь с администратором."),
#                     reply_markup=types.ReplyKeyboardMarkup(
#                         keyboard=[[KeyboardButton("/start")]],
#                         resize_keyboard=True
#                     ),
#                 )

#     except Exception as e:
#         print(e)


@dp.message_handler(commands=["start"], state="*")
async def cmd_start(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    try:
        # Сначала проверяем, есть ли пользователь в EDUBot и получаем его статус:
        user_status = await user_exists(
            message.from_user.id, 
            message.from_user.full_name, 
            message.from_user.mention
        )

        match user_status:
            case TelegramUser.STATE_ACTIVE:
                # Если пользователь уже "активен" в EDUBot, показываем основное меню.
                await show_main_menu(message)

            case TelegramUser.STATE_NOT_ACTIVE:
                title, content, photo = await load_bot_logo("welcome_logo", message.from_user.id)
                media = types.InputFile(photo)
                await message.answer_photo(
                    photo=media,
                    caption=(
                        f"Добро пожаловать,\n"
                        f"в корпоративный бот!\n\n"
                        f"Пожалуйста, выберите язык:\n"
                    ),
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton("🇷🇺Русский")]],
                        resize_keyboard=True,
                    ),
                )
                await LocaleRegSteps.set_language.set()

            case TelegramUser.STATE_DELETED:
                await message.answer(
                    text=_("Ваша учетная запись заблокирована. Для получения дополнительной информации свяжитесь с администратором."),
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton("/start")]],
                        resize_keyboard=True
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
                                # KeyboardButton("🇺🇿O'zbek"),
                                # KeyboardButton("🇬🇧English"),
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