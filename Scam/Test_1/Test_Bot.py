import asyncio
import logging
from aiogram import Dispatcher, Bot, types
from aiogram.filters import Command, CommandObject, CommandStart
from datetime import datetime
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text, Bold
import re
from aiogram.types import Message, FSInputFile, URLInputFile, BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from random import randint
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from magic_filter import F
from aiogram.utils.callback_answer import CallbackAnswerMiddleware, CallbackAnswer


# from config_reader import config

logging.basicConfig(level=logging.INFO)

# bot = Bot(token=config.bot_token.get_secret_value())

bot = Bot(token="6686307025:AAFz1tjuBXs3_4m6eAUBII2B5I5j3GPj4uE", parse_mode="HTML")
dp = Dispatcher()
dp.callback_query.middleware(CallbackAnswerMiddleware())

################

# dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# @dp.message(Command('add_to_list'))
# async def cmd_add_to_list(message: Message, mylist:list[int]):
#     mylist.append(7)
#     await message.answer('add 7')

# @dp.message(Command('show_list'))
# async def cmd_show_list(message: types.Message, mylist:list[int]):
#     await message.answer(f'Your list: {mylist}')

# @dp.message(Command('info'))
# async def cmd_info(message: types.Message, started_at: str):
#     await message.answer(f'Bot start: {started_at}')

################

# @dp.message(Command('hello'))
# async def cmd_hello(message: types.Message):
#     await message.answer(
#         f'Hello, {message.from_user.full_name}'
#     )

################

# @dp.message(Command('settimer'))
# async def cmd_settimer(
#     message: types.Message,
#     command: CommandObject):
#     if command.args is None:
#         await message.answer(
#             'Error: dont'
#         )
#         return
#     try:
#         delay_time, text_to_send = command.args.split (' ', maxsplit=1)
#     except ValueError:
#         await message.answer(
#             "Ошибка: неправильный формат команды. Пример:\n"
#             "/settimer <time> <message>"
#         )
#         return
#     await message.answer(
#         "Таймер добавлен!\n"
#         f"Время: {delay_time}\n"
#         f"Текст: {text_to_send}"
#     )

################

# @dp.message(Command("help"))
# @dp.message(CommandStart(
#     deep_link=True, magic=F.args == "help"
# ))
# async def cmd_start_help(message: Message):
#     await message.answer("Это сообщение со справкой")


# @dp.message(CommandStart(
#     deep_link=True,
#     magic=F.args.regexp(re.compile(r'book_(\d+)'))
# ))
# async def cmd_start_book(
#         message: Message,
#         command: CommandObject
# ):
#     book_number = command.args.split("_")[1]
#     await message.answer(f"Sending book №{book_number}")

################

# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     kb = [
#         [
#             types.KeyboardButton(text="С пюрешкой"),
#             types.KeyboardButton(text="Без пюрешки")
#         ]
#     ]
#     keyboard = types.ReplyKeyboardMarkup(
#         keyboard=kb,
#         resize_keyboard=True,
#         input_field_placeholder='Выберите способ подачи'
#         )
#     await message.answer("Как подавать котлеты?", reply_markup=keyboard)

# @dp.message(F.text.lower() == "с пюрешкой")
# async def with_puree(message: types.Message):
#     await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())

# @dp.message(F.text.lower() == "без пюрешки")
# async def without_puree(message: types.Message):
#     await message.reply("Так невкусно!", reply_markup=types.ReplyKeyboardRemove())

################

# @dp.message(Command("reply_builder"))
# async def reply_builder(message: types.Message):
#     builder = ReplyKeyboardBuilder()
#     for i in range(1, 17):
#         builder.add(types.KeyboardButton(text=str(i)))
#     builder.adjust(4)
#     await message.answer(
#         "Выберите число:",
#         reply_markup=builder.as_markup(resize_keyboard=True),
#     )

################

# @dp.message(Command('special_buttons'))
# async def cmd_special_buttons(message: Message):
#     builder = ReplyKeyboardBuilder
#     builder.row(
#         types.KeyboardButton(text='Запросить геолокацию', request_location=True),
#         types.KeyboardButton(text='Запросить контакт', request_contact=True)
#     )
#     builder.row(types.KeyboardButton(
#         text="Создать викторину",
#         request_poll=types.KeyboardButtonPollType(type="quiz"))
#     )
#     builder.row(
#         types.KeyboardButton(
#             text="Выбрать премиум пользователя",
#             request_user=types.KeyboardButtonRequestUser(
#                 request_id=1,
#                 user_is_premium=True
#             )
#         ),
#         types.KeyboardButton(
#             text="Выбрать супергруппу с форумами",
#             request_chat=types.KeyboardButtonRequestChat(
#                 request_id=2,
#                 chat_is_channel=False,
#                 chat_is_forum=True
#             )
#         )
#     )

#     await message.answer(
#         "Выберите действие:",
#         reply_markup=builder.as_markup(resize_keyboard=True),
#     )

# @dp.message(F.user_shared)
# async def on_user_shared(message: types.Message):
#     print(
#         f"Request {message.user_shared.request_id}. "
#         f"User ID: {message.user_shared.user_id}"
#     )


# @dp.message(F.chat_shared)
# async def on_user_shared(message: types.Message):
#     print(
#         f"Request {message.chat_shared.request_id}. "
#         f"User ID: {message.chat_shared.chat_id}"
#     )

################

# @dp.message(Command("inline_url"))
# async def cmd_inline_url(message: types.Message, bot: Bot):
#     builder = InlineKeyboardBuilder()
#     builder.row(types.InlineKeyboardButton(
#         text="GitHub", url="https://github.com")
#     )
#     builder.row(types.InlineKeyboardButton(
#         text="Оф. канал Telegram",
#         url="tg://resolve?domain=telegram")
#     )

#     # Чтобы иметь возможность показать ID-кнопку,
#     # У юзера должен быть False флаг has_private_forwards
#     user_id = 1234567890
#     chat_info = await bot.get_chat(user_id)
#     if not chat_info.has_private_forwards:
#         builder.row(types.InlineKeyboardButton(
#             text="Какой-то пользователь",
#             url=f"tg://user?id={user_id}")
#         )

#     await message.answer(
#         'Выберите ссылку',
#         reply_markup=builder.as_markup(),
#     )

################

# @dp.message(Command('random'))
# async def cmd_random(message: Message):
#     builder = InlineKeyboardBuilder()
#     builder.add(types.InlineKeyboardButton(
#         text='Нажми меня',
#         callback_data='random_value')
#     )
#     await message.answer(
#         'Нажмите на кнопку, чтобы бот отправил число от 1 до 10',
#         reply_markup=builder.as_markup()
#     )

# @dp.callback_query(F.data == 'random_value')
# async def send_random_value(callback: types.CallbackQuery):
#     await callback.message.answer(str(randint(1, 10)))
#     await callback.answer()

################

# user_data = {}

# def get_keyboard():
#     buttons = [
#         [
#             types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
#             types.InlineKeyboardButton(text="+1", callback_data="num_incr")
#         ],
#         [types.InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")]
#     ]
#     keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
#     return keyboard


# async def update_num_text(message: types.Message, new_value: int):
#     with suppress(TelegramBadRequest):
#         await message.edit_text(
#             f"Укажите число: {new_value}",
#             reply_markup=get_keyboard()
#         )


# @dp.message(Command("numbers"))
# async def cmd_numbers(message: types.Message):
#     user_data[message.from_user.id] = 0
#     await message.answer("Укажите число: 0", reply_markup=get_keyboard())


# @dp.callback_query(F.data.startswith("num_"))
# async def callbacks_num(callback: types.CallbackQuery):
#     user_value = user_data.get(callback.from_user.id, 0)
#     action = callback.data.split("_")[1]

#     if action == "incr":
#         user_data[callback.from_user.id] = user_value+1
#         await update_num_text(callback.message, user_value+1)
#     elif action == "decr":
#         user_data[callback.from_user.id] = user_value-1
#         await update_num_text(callback.message, user_value-1)
#     elif action == "finish":
#         await callback.message.edit_text(f"Итого: {user_value}")

#     await callback.answer()

################

# user_data = {}

# class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
#     action: str
#     value: Optional[int] = None

# def get_keyboard_fab():
#     builder = InlineKeyboardBuilder()
#     builder.button(
#         text='-2', callback_data=NumbersCallbackFactory(action='change', value=-2)
#     )
#     builder.button(
#         text="-1", callback_data=NumbersCallbackFactory(action="change", value=-1)
#     )
#     builder.button(
#         text="+1", callback_data=NumbersCallbackFactory(action="change", value=1)
#     )
#     builder.button(
#         text="+2", callback_data=NumbersCallbackFactory(action="change", value=2)
#     )
#     builder.button(
#         text="Подтвердить", callback_data=NumbersCallbackFactory(action="finish")
#     )

#     builder.adjust(4)
#     return builder.as_markup()

# async def update_num_text_fab(message: types.Message, new_value: int):
#     with suppress(TelegramBadRequest):
#         await message.edit_text(
#             f"Укажите число: {new_value}",
#             reply_markup=get_keyboard_fab()
#         )

# @dp.message(Command("numbers_fab"))
# async def cmd_numbers_fab(message: types.Message):
#     user_data[message.from_user.id] = 0
#     await message.answer("Укажите число: 0", reply_markup=get_keyboard_fab())

# async def update_num_text_fab(message: types.Message, new_value: int):
#     with suppress(TelegramBadRequest):
#         await message.edit_text(
#             f"Укажите число: {new_value}",
#             reply_markup=get_keyboard_fab()
#         )

# @dp.message(Command("numbers_fab"))
# async def cmd_numbers_fab(message: types.Message):
#     user_data[message.from_user.id] = 0
#     await message.answer("Укажите число: 0", reply_markup=get_keyboard_fab())

# @dp.callback_query(NumbersCallbackFactory.filter())
# async def callbacks_num_change_fab(
#         callback: types.CallbackQuery, 
#         callback_data: NumbersCallbackFactory
# ):
#     # Текущее значение
#     user_value = user_data.get(callback.from_user.id, 0)
#     # Если число нужно изменить
#     if callback_data.action == "change":
#         user_data[callback.from_user.id] = user_value + callback_data.value
#         await update_num_text_fab(callback.message, user_value + callback_data.value)
#     # Если число нужно зафиксировать
#     else:
#         await callback.message.edit_text(f"Итого: {user_value}")
#     await callback.answer()

# # Нажатие на одну из кнопок: -2, -1, +1, +2
# @dp.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
# async def callbacks_num_change_fab(
#         callback: types.CallbackQuery, 
#         callback_data: NumbersCallbackFactory
# ):
#     # Текущее значение
#     user_value = user_data.get(callback.from_user.id, 0)

#     user_data[callback.from_user.id] = user_value + callback_data.value
#     await update_num_text_fab(callback.message, user_value + callback_data.value)
#     await callback.answer()


# # Нажатие на кнопку "подтвердить"
# @dp.callback_query(NumbersCallbackFactory.filter(F.action == "finish"))
# async def callbacks_num_finish_fab(callback: types.CallbackQuery):
#     # Текущее значение
#     user_value = user_data.get(callback.from_user.id, 0)

#     await callback.message.edit_text(f"Итого: {user_value}")
#     await callback.answer()

################





################################################    

async def main():
    await dp.start_polling(bot, mylist=[1, 2, 3])


if __name__ == "__main__":
    asyncio.run(main())
