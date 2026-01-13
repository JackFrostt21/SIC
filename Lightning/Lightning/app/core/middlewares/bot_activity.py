import logging
import re
from typing import Any, Dict, Optional, Tuple

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from asgiref.sync import sync_to_async
from django.utils import timezone

from app.core.models import BotEventLog

logger = logging.getLogger(__name__)


def _parse_callback(raw: str) -> Tuple[str, Dict[str, Any], str]:
    """
    Разбор callback_data в человекочитаемый вид.

    - action_key: краткий ключ действия, например: 'callback:open_lightning'
    - data: словарь распознанных параметров (числа приводим к int)
    - human_text: строка для админки вида 'open_lightning: lightning_id=123'
    """
    if not raw:
        return "callback:unknown", {}, "callback:unknown"

    # Формат Aiogram CallbackData: 'prefix:key1:value1:key2:value2'
    parts = raw.split(":")
    prefix = parts[0] if parts else "unknown"
    data: Dict[str, Any] = {}

    # Пробуем распарсить попарно: key, value
    tail = parts[1:]
    if len(tail) >= 2:
        for i in range(0, len(tail) - 1, 2):
            key = tail[i]
            value = tail[i + 1]
            if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                try:
                    data[key] = int(value)
                except Exception:
                    data[key] = value
            else:
                data[key] = value
    else:
        # Фоллбэк: ищем пары 'k=v'
        pairs = re.findall(r"(\w+)=([\w-]+)", raw or "")
        for k, v in pairs:
            if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
                try:
                    data[k] = int(v)
                except Exception:
                    data[k] = v
            else:
                data[k] = v

    action_key = f"callback:{prefix or 'unknown'}"

    # Человекочитаемый текст
    if data:
        kv = ", ".join([f"{k}={v}" for k, v in data.items()])
        human_text = f"{prefix}: {kv}"
    else:
        human_text = prefix

    return action_key, data, human_text


def _classify_message(msg: Message) -> Tuple[str, str, Optional[str]]:
    """
    Возвращает (event_type, action_key, content_text) для Message.
    - Команды помечаем как 'command:/start'
    - Обычный текст: 'message:text'
    - Вложения: contact/document/photo/location
    """
    if msg.text and msg.text.startswith("/"):
        return "command", f"command:{msg.text.split()[0]}", msg.text

    if msg.text:
        return "message", "message:text", msg.text

    if msg.contact:
        return "message", "message:contact", None
    if msg.document:
        name = msg.document.file_name or "document"
        return "message", "message:document", f"[document:{name}]"
    if msg.photo:
        return "message", "message:photo", "[photo]"
    if getattr(msg, "location", None):
        return "message", "message:location", "[location]"

    return "message", "message:unknown", None


class ActivityLogMiddleware(BaseMiddleware):
    """Мидлварь логирования активности пользователей бота.

    Что делает:
    - Логирует входящие Message и CallbackQuery в модель BotEventLog
    - Обновляет TelegramUser.last_activity (Дата) на каждое событие
    - Не ломает обработку: все исключения внутри мидлвари перехватываются
    """

    async def __call__(self, handler, event: Update, data: Dict[str, Any]):  # type: ignore[override]
        # Оборачиваем вызов хендлера, чтобы при ошибках записать error-лог
        try:
            await self._log_event_safe(event, data)
        except Exception:
            # Никогда не прерываем цепочку из-за логирования
            logger.exception("ActivityLogMiddleware: ошибка при логировании события")

        try:
            return await handler(event, data)
        except Exception as e:
            # Пишем error-событие и пробрасываем дальше
            try:
                await self._log_error_safe(event, data, e)
            except Exception:
                logger.exception(
                    "ActivityLogMiddleware: ошибка при логировании исключения"
                )
            raise

    async def _log_event_safe(self, event: Update, data: Dict[str, Any]) -> None:
        # Определяем тип апдейта: message / callback_query
        is_private = True
        telegram_id: Optional[int] = None
        username: Optional[str] = None
        chat_id: Optional[int] = None
        update_id: Optional[int] = getattr(event, "update_id", None)
        event_type: str = "system"
        action_key: str = "system:unknown"
        content_text: Optional[str] = None
        detail_data: Dict[str, Any] = {}

        if event.message:
            msg = event.message
            event_type, action_key, content_text = _classify_message(msg)
            telegram_id = msg.from_user.id if msg.from_user else None
            username = msg.from_user.username if msg.from_user else None
            chat_id = msg.chat.id if msg.chat else None
            is_private = getattr(msg.chat, "type", None) == "private"
        elif event.callback_query:
            cq = event.callback_query
            event_type = "callback"
            telegram_id = cq.from_user.id if cq.from_user else None
            username = cq.from_user.username if cq.from_user else None
            chat_id = cq.message.chat.id if cq.message and cq.message.chat else None
            is_private = (
                (getattr(cq.message.chat, "type", None) == "private")
                if cq.message and cq.message.chat
                else True
            )

            # Парсим callback_data
            action_key, detail_data, human_text = _parse_callback(cq.data or "")
            content_text = human_text
        else:
            # Прочие типы апдейтов сейчас не логируем
            return

        # Пытаемся получить текущий FSM-стейт (если доступен в data)
        state_name: Optional[str] = None
        try:
            fsm = data.get("state")
            if fsm:
                state_name = await fsm.get_state()
        except Exception:
            state_name = None

        # Пытаемся получить хендлер (если доступен в data)
        handler_name: Optional[str] = None
        try:
            h = data.get("handler")
            if h:
                handler_name = getattr(h, "__qualname__", None) or getattr(
                    h, "__name__", None
                )
        except Exception:
            handler_name = None

        # Находим пользователя и обновляем last_activity (дата)
        user_obj = await self._get_user_and_touch_activity(telegram_id)

        # Сохраняем лог
        await sync_to_async(BotEventLog.objects.create)(
            user=user_obj,
            telegram_id=telegram_id or 0,
            username=username,
            chat_id=chat_id,
            update_id=update_id,
            event_type=event_type,
            action_key=action_key,
            content_text=content_text,
            data=detail_data or None,
            handler=handler_name,
            state=state_name,
            is_private=is_private,
        )

    async def _log_error_safe(
        self, event: Update, data: Dict[str, Any], exc: Exception
    ) -> None:
        # Минимальная информация об ошибке
        telegram_id = None
        username = None
        chat_id = None
        update_id = getattr(event, "update_id", None)
        is_private = True

        if event.message:
            msg = event.message
            telegram_id = msg.from_user.id if msg.from_user else None
            username = msg.from_user.username if msg.from_user else None
            chat_id = msg.chat.id if msg.chat else None
            is_private = getattr(msg.chat, "type", None) == "private"
        elif event.callback_query:
            cq = event.callback_query
            telegram_id = cq.from_user.id if cq.from_user else None
            username = cq.from_user.username if cq.from_user else None
            chat_id = cq.message.chat.id if cq.message and cq.message.chat else None
            is_private = (
                (getattr(cq.message.chat, "type", None) == "private")
                if cq.message and cq.message.chat
                else True
            )

        user_obj = await self._get_user_and_touch_activity(telegram_id)

        await sync_to_async(BotEventLog.objects.create)(
            user=user_obj,
            telegram_id=telegram_id or 0,
            username=username,
            chat_id=chat_id,
            update_id=update_id,
            event_type="error",
            action_key="error:exception",
            content_text=str(exc),
            data=None,
            handler=None,
            state=None,
            is_private=is_private,
        )

    async def _get_user_and_touch_activity(self, telegram_id: Optional[int]):
        """Возвращает TelegramUser (если найден) и обновляет last_activity (только дату)."""
        if not telegram_id:
            return None

        from app.bot.models.telegramuser_models import TelegramUser  # локальный импорт

        def _get_and_touch() -> Optional[TelegramUser]:  # type: ignore[name-defined]
            user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
            if user:
                # Обновляем только дату
                user.last_activity = timezone.now().date()
                user.save(update_fields=["last_activity"])
            return user

        return await sync_to_async(_get_and_touch)()
