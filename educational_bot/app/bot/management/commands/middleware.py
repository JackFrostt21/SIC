from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from asgiref.sync import sync_to_async
from app.bot.models.telegram_user import UserAction


class LoggingMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        await self.log_action(message.from_user, "message", message.text)

    async def on_process_callback_query(self, call: types.CallbackQuery, data: dict):
        await self.log_action(call.from_user, "callback_query", call.data)

    @sync_to_async
    def log_action(self, user, action_type, action_details):
        UserAction.objects.create(
           user = user.full_name or user.username or str(user.id),
           action_type = action_type,
           action_details = action_details
        )