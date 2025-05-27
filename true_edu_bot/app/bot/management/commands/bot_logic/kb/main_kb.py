from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from asgiref.sync import sync_to_async
from aiogram import types
from app.bot.management.commands.bot_logic.lang_middleware import setup_middleware
from app.bot.management.commands.loader import dp

i18n = setup_middleware(dp)
_ = i18n.gettext


@sync_to_async
def building_main_menu(user_id):
    print(user_id)
    web_app_url_info = types.WebAppInfo(url="https://educationalbot.engsdrilling.ru/api/testing-testing_module/bot-info/")
    web_app_url_progress = types.WebAppInfo(url=f"https://educationalbot.engsdrilling.ru/api/testing-testing_module/progress/?user_id={user_id}")
    # https://127.0.0.1:8000/
    # https://educationalbot.engsdrilling.ru/

    menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(_("self-study"))
    ).add(
        KeyboardButton(text="Моя статистика", web_app=web_app_url_progress),
        KeyboardButton(text="О боте", web_app=web_app_url_info)
    )

    return menu_keyboard