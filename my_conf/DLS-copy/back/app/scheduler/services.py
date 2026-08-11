"""
Сервис рассылки напоминаний о непройденных курсах.

send_unfinished_courses() — синхронная оболочка, безопасная для вызова из планировщика.
Логика:
- Берём активных Telegram пользователей (state=1, telegram_id > 0).
- Получаем список доступных курсов через CourseRepository.get_available_courses.
- Отбираем курсы, где тест не сдан (test_status != 'completed_passed').
- Отправляем пользователю список этих курсов кнопками `course:<id>` (у бота уже есть хендлеры).
"""

import asyncio
import logging
from typing import Dict, List

from django.conf import settings as django_settings

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import FSInputFile, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

logger = logging.getLogger(__name__)


def send_unfinished_courses() -> Dict[str, int]:
    """Синхронная оболочка для асинхронной рассылки."""
    return asyncio.run(_send_unfinished_courses_async())


async def _send_unfinished_courses_async() -> Dict[str, int]:
    from app.bot.models.telegram_user import TelegramUser
    from app.learning_app.repositories.course_repository import CourseRepository
    from app.scheduler.models import ReminderSetting

    total_messages_sent = 0
    total_errors = 0

    settings_obj = await asyncio.to_thread(ReminderSetting.objects.first)
    batch_size = settings_obj.batch_size if settings_obj else 25
    delay_between_users = settings_obj.delay_between_users if settings_obj else 0.15
    delay_between_batches = settings_obj.delay_between_batches if settings_obj else 3
    max_retry_attempts = settings_obj.max_retry_attempts if settings_obj else 5
    enable_gif = settings_obj.enable_gif if settings_obj else False
    gif_path = settings_obj.gif.path if settings_obj and settings_obj.gif else None

    bot = Bot(
        token=django_settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    course_repo = CourseRepository()

    try:
        users_qs = TelegramUser.objects.filter(state=1, telegram_id__isnull=False).exclude(
            telegram_id__lte=0
        )
        users: List[TelegramUser] = await asyncio.to_thread(list, users_qs)
        logger.info("reminder: candidates -> %s users", len(users))
    except Exception:
        logger.exception("Ошибка получения пользователей для напоминаний")
        await _safe_close_bot(bot)
        return {"total_messages_sent": 0, "total_errors": 0}

    failed_users: List[int] = []

    for i in range(0, len(users), batch_size):
        batch_users = users[i : i + batch_size]
        for user in batch_users:
            try:
                courses = await course_repo.get_available_courses(user.telegram_id)
                unfinished = [
                    c for c in courses if c.get("test_status") != "completed_passed"
                ]
                if not unfinished:
                    continue

                kb = InlineKeyboardBuilder()
                for item in unfinished:
                    course = item["course"]
                    test_status = item.get("test_status")
                    prefix = ""
                    if test_status == "completed_failed":
                        prefix = "❌ "
                    title = f"{prefix}{course.title}"
                    kb.button(text=f"📚 {title}", callback_data=f"course:{course.id}")
                kb.adjust(1)

                # GIF перед текстом (опционально)
                if enable_gif and gif_path:
                    try:
                        await bot.send_animation(
                            chat_id=user.telegram_id,
                            animation=FSInputFile(gif_path),
                        )
                        total_messages_sent += 1
                    except Exception:
                        logger.warning("GIF: не удалось отправить пользователю %s", user.telegram_id)

                text = (
                    "У вас есть непройденные курсы. "
                    "Выберите курс, чтобы продолжить обучение:"
                )
                await bot.send_message(
                    user.telegram_id,
                    text,
                    reply_markup=kb.as_markup(),
                )
                total_messages_sent += 1
                await asyncio.sleep(delay_between_users)
            except TelegramRetryAfter as e:
                await asyncio.sleep(getattr(e, "retry_after", 1))
                total_errors += 1
                failed_users.append(user.id)
            except (TelegramForbiddenError, TelegramBadRequest, TelegramNetworkError):
                total_errors += 1
            except Exception:
                logger.exception(
                    "Ошибка отправки напоминания пользователю %s", user.telegram_id
                )
                total_errors += 1

        if i + batch_size < len(users):
            await asyncio.sleep(delay_between_batches)

    # Повторные попытки для пользователей с retry-after/сетевыми ошибками
    attempt = 2
    while failed_users and attempt <= max_retry_attempts:
        backoff = min(30, 2**attempt)
        await asyncio.sleep(backoff)

        still_failed: List[int] = []
        for i in range(0, len(failed_users), batch_size):
            batch_ids = failed_users[i : i + batch_size]
            batch_users = await asyncio.to_thread(
                lambda: list(TelegramUser.objects.filter(id__in=batch_ids))
            )
            for user in batch_users:
                try:
                    courses = await course_repo.get_available_courses(user.telegram_id)
                    unfinished = [
                        c for c in courses if c.get("test_status") != "completed_passed"
                    ]
                    if not unfinished:
                        continue

                    kb = InlineKeyboardBuilder()
                    for item in unfinished:
                        course = item["course"]
                        kb.button(
                            text=f"📚 {course.title}",
                            callback_data=f"course:{course.id}",
                        )
                    kb.adjust(1)

                    await bot.send_message(
                        user.telegram_id,
                        "У вас есть непройденные курсы. Выберите курс:",
                        reply_markup=kb.as_markup(),
                    )
                    total_messages_sent += 1
                    await asyncio.sleep(delay_between_users)
                except TelegramRetryAfter as e:
                    await asyncio.sleep(getattr(e, "retry_after", 1))
                    total_errors += 1
                    still_failed.append(user.id)
                except (TelegramForbiddenError, TelegramBadRequest, TelegramNetworkError):
                    total_errors += 1
                except Exception:
                    logger.exception(
                        "Ошибка повторной отправки пользователю %s", user.telegram_id
                    )
                    total_errors += 1

            if i + batch_size < len(failed_users):
                await asyncio.sleep(delay_between_batches)

        failed_users = still_failed
        attempt += 1

    await _safe_close_bot(bot)

    return {
        "total_messages_sent": total_messages_sent,
        "total_errors": total_errors,
    }


async def _safe_close_bot(bot: Bot) -> None:
    try:
        await bot.session.close()
    except Exception:
        pass
