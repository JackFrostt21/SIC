import asyncio
from aiogram import Bot, Dispatcher
from handlers import questions, different_types

async def main():
    bot = Bot(token="6686307025:AAFz1tjuBXs3_4m6eAUBII2B5I5j3GPj4uE")
    dp = Dispatcher()

    dp.include_routers(questions.router, different_types.router)

    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())