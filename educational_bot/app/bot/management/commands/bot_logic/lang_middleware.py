from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from typing import Tuple, Any

from asgiref.sync import sync_to_async

from app.bot.models.telegram_user import TelegramUser
from app.settings import BASE_DIR

I18N_DOMAIN = 'django'
LOCALES_DIR = BASE_DIR / 'locale/'


@sync_to_async
def get_lang(user_id):
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        if user:
            return user.language
        # else:
        #     return None
    except Exception as e:
        print(e)
        print('языка нет')
        return None


class UserLocaleMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):
        user = types.User.get_current()
        return await get_lang(user.id) or 'ru'  # self.default


def setup_middleware(dp):
    i18n = UserLocaleMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
