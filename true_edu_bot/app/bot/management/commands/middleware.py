from aiogram import types
from django.db.utils import IntegrityError
import logging
from aiogram.dispatcher.middlewares import BaseMiddleware
from asgiref.sync import sync_to_async
from app.bot.models.telegram_user import UserAction, TelegramUser


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        await self.log_action(message.from_user, "message", message.text)

    async def on_process_callback_query(self, call: types.CallbackQuery, data: dict):
        await self.log_action(call.from_user, "callback_query", call.data)

    @sync_to_async
    def log_action(self, user, action_type, action_details):
        pass
        # try:
        #     telegram_user, created = TelegramUser.objects.get_or_create(
        #         user_id=user.id,
        #         defaults={
        #             'username': user.username,
        #             'first_name': user.first_name,
        #             'last_name': user.last_name,
        #         }
        #     )
        #     UserAction.objects.create(
        #         user=telegram_user,
        #         action_type=action_type,
        #         action_details=action_details
        #     )
        # except IntegrityError as e:
        #     logger.error(f"Ошибка сохранения действия пользователя: {e}")