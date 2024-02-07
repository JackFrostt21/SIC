import asyncio
import logging
from aiogram import Bot, Dispatcher
from django.core.management import BaseCommand
from .handlers import application_handlers, start_handlers, email_handlers

logging.basicConfig(level=logging.INFO)

API_TOKEN = '6686307025:AAFz1tjuBXs3_4m6eAUBII2B5I5j3GPj4uE'

# bot = Bot(token=API_TOKEN)
# dp = Dispatcher()

# ### ДОБАВИТЬ КОМАНДЫ В МЕНЮ!!!


# # dp.include_router(start_handlers.router)
# dp.include_router(email_handlers.router)
# dp.include_router(application_handlers.router)

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(email_handlers.router)
    dp.include_router(application_handlers.router)

    await dp.start_polling(bot)

class Command (BaseCommand):
    asyncio.run(main())


# if __name__ == '__main__':
#     asyncio.run(main())