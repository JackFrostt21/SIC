import asyncio
import logging
from aiogram import Dispatcher, Bot, types
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)

bot = Bot(token='6686307025:AAFz1tjuBXs3_4m6eAUBII2B5I5j3GPj4uE')
dp = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Hello!')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
