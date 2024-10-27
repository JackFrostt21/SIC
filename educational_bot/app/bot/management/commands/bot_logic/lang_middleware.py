from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from typing import Tuple, Any

from asgiref.sync import sync_to_async

from app.bot.models.telegram_user import TelegramUser
from app.settings import BASE_DIR

I18N_DOMAIN = 'django'
LOCALES_DIR = BASE_DIR / 'locale/'


"""
Эта функция асинхронно получает язык пользователя из базы данных. 
Она ищет пользователя по user_id и возвращает его язык (user.language). 
Если пользователь не найден или возникает ошибка, функция возвращает None и выводит сообщение об ошибке.
"""
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
        return None

"""
Получаем текущего пользователя, получаем язык пользователя из БД
Если язык найден, возвращаем, если нет, то по умолчанию 'ru'
"""
class UserLocaleMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):
        user = types.User.get_current()
        return await get_lang(user.id) or 'ru'  # self.default

"""
Эта функция настраивает middleware для бота:
Создает экземпляр UserLocaleMiddleware с доменом локализации (I18N_DOMAIN) и директорией локалей (LOCALES_DIR).
Устанавливает этот middleware в диспетчер (dp.middleware.setup(i18n)).
Возвращает экземпляр middleware.
"""
def setup_middleware(dp):
    i18n = UserLocaleMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
