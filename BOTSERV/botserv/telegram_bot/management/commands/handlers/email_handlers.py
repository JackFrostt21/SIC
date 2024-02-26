import aiohttp
import re
from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async


from telegram_bot.models import TelegramUser


import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


router = Router()


class EmailState(StatesGroup):
    waiting_for_email = State()


email_check = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


@sync_to_async
def get_user_by_telegram_id(id):
    return TelegramUser.objects.filter(number_user_telegram=id).first() 


@sync_to_async
def create_user(id, email):
    user, created = TelegramUser.objects.get_or_create(number_user_telegram=id, defaults={'email': email})
    return user



async def send_data_to_external_api(user_data):
    ### урл и хэдер можно вывести в отдельный класс и обращаться к элементам, но не факт что нужно
    url = 'https://services.eriell.com/api/tgBot/setId'
    headers = {
        'Authorization': 'Basic dGVtcC51c2VyQHRlbXAudXNlcjp6NXMyWW5BNQ=='
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=user_data, headers=headers) as response:
                response_data = await response.json()
                return response_data
        except Exception as e:
            return None


@router.message(Command('start'))
async def send_welcome(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        if user.user_eriell:
            await message.answer('Вы уже зарегистрированы, нажмите в меню /zayavka для работы с заявками или /spisok для вывода всех ваших заявок')
        else:
            await message.answer('Вам необходимо подтвердить email - services.eriell.com')
    else:
        await message.answer('Привет! Пожалуйста, введите ваш email.')
        await state.set_state(EmailState.waiting_for_email)


@router.message(StateFilter(EmailState.waiting_for_email))
async def email_received(message: types.Message, state: FSMContext):
    if email_check.fullmatch(message.text):
        # Создаем пользователя в нашей системе до отправки данных во внешний API
        user = await create_user(message.from_user.id, message.text)
        if user:
            # Данные для отправки в Диму
            user_data = {
                "id": user.id,
                "email": message.text,
                "number_user_telegram": str(message.from_user.id),
            }
            # Отправляем данные в Диму
            response_data = await send_data_to_external_api(user_data)

            # Проверка ответа
            if response_data and response_data.get("ok") == 1:
                await message.answer('Для завершения регистрации вам необходимо подтвердить ваш email - services.eriell.com')
            else:
                # Обработка ошибок 
                error_message = {
                    -1: 'Ошибка на стороне services.eriell.com, пожалуйста, попробуйте выполнить регистрацию позже',
                    -2: 'Пользователь с указанным email не существует в services.eriell.com, предварительно необходимо получить доступ к services.eriell.com',
                    -3: 'Ваш телеграмм пользователь уже привязан к другому аккаунту (email) в services.eriell.com',
                }.get(response_data.get("ok"), 'Неизвестная ошибка при регистрации. Пожалуйста, попробуйте выполнить регистрацию позже')
                await message.answer(error_message)
        else:
            await message.answer('Произошла ошибка: пользователь уже зарегистрирован')
        await state.clear()
    else:
        await message.answer('Пожалуйста, введите корректный email.')

    

