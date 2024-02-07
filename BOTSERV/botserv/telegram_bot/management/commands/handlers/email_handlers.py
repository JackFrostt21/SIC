from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
import re

from telegram_bot.models import TelegramUser


router = Router()


class EmailState(StatesGroup):
    waiting_for_email = State()


email_check = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


@sync_to_async
def get_user_by_telegram_username(username):
    return TelegramUser.objects.filter(username_telegram=username).first() 


@sync_to_async
def create_user_if_not_exists(username, email):
    if not TelegramUser.objects.filter(username_telegram=username).exists():
        TelegramUser.objects.create(username_telegram=username, email=email)
        return True
    return False


@router.message(Command('start'))
async def send_welcome(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_username(message.from_user.username)
    if user:
        if user.user_eriell:
            await message.answer('Вы уже зарегистрированы, нажмите в меню zayavki для работы с заявками или spisok для вывода всех ваших заявок')
        else:
            await message.answer('Вам необходимо подтвердить email - services.eriell.com')
    else:
        await message.answer('Привет! Пожалуйста, введите ваш email.')
        await state.set_state(EmailState.waiting_for_email)


@router.message(StateFilter(EmailState.waiting_for_email))
async def email_received(message: types.Message, state: FSMContext):
    if email_check.fullmatch(message.text):
        user_created = await create_user_if_not_exists(message.from_user.username, message.text)
        if user_created:
            await message.answer('Для завершения регистрации вам необходимо подтвердить ваш email - services.eriell.com')
        else:
            await message.answer('Вы уже зарегистрированы.')
        await state.clear()
    else:
        await message.answer('Пожалуйста, введите корректный email.')        