# from aiogram import Router
# from aiogram.types import Message
# from aiogram.filters import Command
# from asgiref.sync import sync_to_async
# from telegram_bot.models import User

# router = Router()

# #получаем юзернейм пользователя и проверяем его в БД, если найден, берем первого, если нет то возвращаем None
# @sync_to_async
# def get_user_by_telegram_username(username):
#     return User.objects.filter(username_telegram=username).first()

# @router.message(Command('start'))
# async def send_welcome(message: Message):
#     user = await get_user_by_telegram_username(message.from_user.username)
#     if user:
#         await message.answer('Привет! Вы уже зарегистрированы.')
#     else:
#         await message.answer('Привет! Пожалуйста, введите ваш email.')


# import re
# from aiogram import Router
# from aiogram.types import Message
# from asgiref.sync import sync_to_async
# from telegram_bot.models import User

# router = Router()

# email_check = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# @sync_to_async
# def create_user_if_not_exists(username, email):
#     if not User.objects.filter(username_telegram=username).exists():
#         User.objects.create(username_telegram=username, email=email, active=True)

# @router.message()
# async def email_received(message: Message):
#     if email_check.fullmatch(message.text):
#         user_created = await create_user_if_not_exists(message.from_user.username, message.text)
#         if user_created:
#             await message.answer('Учетная запись успешно активирована.')
#         else:
#             await message.answer('Вы уже зарегистрированы.')
#     else:
#         await message.answer('Пожалуйста, введите действительный email.')