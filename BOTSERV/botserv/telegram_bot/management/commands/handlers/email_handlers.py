from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
import re


from telegram_bot.models import TelegramUser


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


router = Router()


class EmailState(StatesGroup):
    waiting_for_email = State()


email_check = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


@sync_to_async
def get_user_by_telegram_id(id):
    return TelegramUser.objects.filter(number_user_telegram=id).first()


@sync_to_async
def create_user(id, email):
    created = TelegramUser.objects.get_or_create(
        number_user_telegram=id, defaults={"email": email}
    )
    return created


@router.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        if user.user_eriell:
            await message.answer(
                "Вы уже зарегистрированы, нажмите в меню /zayavka для работы с заявками или /spisok для вывода всех ваших заявок"
            )
        else:
            await message.answer(
                "Вам необходимо подтвердить email - services.eriell.com"
            )
    else:
        await message.answer("Привет! Пожалуйста, введите ваш email.")
        await state.set_state(EmailState.waiting_for_email)


@router.message(StateFilter(EmailState.waiting_for_email))
async def email_received(message: types.Message, state: FSMContext):
    if email_check.fullmatch(message.text):
        user_created = await create_user(message.from_user.id, message.text)
        if user_created:
            await message.answer(
                "Для завершения регистрации вам необходимо подтвердить ваш email - services.eriell.com"
            )
            ### плюс еще скриншоты, от Димы
        else:
            await message.answer("Вы уже зарегистрированы.")
        await state.clear()
    else:
        await message.answer("Пожалуйста, введите корректный email.")
