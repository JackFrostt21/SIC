"""Сервис рассылки напоминаний о непрочитанных молниях.

Функция send_unread_lightnings() синхронная и безопасна для вызова из планировщика.
Внутри она запускает асинхронную логику отправки через asyncio.run.

Особенности:
- Берёт настройки из LightningSetting (batch_size, задержки, ретраи, enable_gif).
- Находит пользователей, у кого есть непрочитанные молнии (LightningRead.is_read=False).
- Не отправляет «У вас нет новых молний» по крону — просто пропускает такого пользователя.
- Отправляет GIF перед текстом, если enable_gif=True и загружен gif.
"""

import asyncio
import logging
from typing import Dict, List

from django.conf import settings as django_settings

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramRetryAfter,
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramNetworkError,
)
from aiogram.types import FSInputFile

from app.bot.telegram.keyboards.lightning_kb import get_lightnings_list_kb


logger = logging.getLogger(__name__)


def send_unread_lightnings() -> Dict[str, int]:
    """Синхронная оболочка для асинхронной рассылки."""
    return asyncio.run(_send_unread_lightnings_async())


async def _send_unread_lightnings_async() -> Dict[str, int]:
    from app.bot.models.telegramuser_models import TelegramUser
    from app.lightning.models.lightning_setting_models import LightningSetting
    from app.lightning.models.lightning_data_models import LightningRead
    from app.lightning.models.lightning_models import Lightning
    from app.bot.telegram.selectors.lightning_selectors import (
        list_unread_lightnings,
        get_lightnings_status,
    )

    total_messages_sent = 0
    total_errors = 0

    # Загружаем настройки
    settings_obj = await asyncio.to_thread(LightningSetting.objects.first)

    # Значения по умолчанию, если настроек нет
    batch_size = settings_obj.batch_size if settings_obj else 25
    delay_between_users = settings_obj.delay_between_users if settings_obj else 0.15
    delay_between_batches = settings_obj.delay_between_batches if settings_obj else 3
    max_retry_attempts = settings_obj.max_retry_attempts if settings_obj else 5
    enable_gif = settings_obj.enable_gif if settings_obj else False
    gif_path = settings_obj.gif.path if settings_obj and settings_obj.gif else None

    # Инициализируем краткоживущего бота
    bot = Bot(
        token=django_settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Собираем пользователей с непрочитанными молниями
    try:
        user_ids_qs = await asyncio.to_thread(
            lambda: list(
                LightningRead.objects.filter(
                    is_read=False,
                    user__state=1,
                    user__telegram_id__isnull=False,
                )
                .exclude(user__telegram_id__lte=0)
                .values_list("user_id", flat=True)
                .distinct()
            )
        )
        if not user_ids_qs:
            await _safe_close_bot(bot)
            return {
                "total_messages_sent": 0,
                "total_errors": 0,
            }
        users_qs = TelegramUser.objects.filter(
            id__in=user_ids_qs, state=1, telegram_id__isnull=False
        ).exclude(telegram_id__lte=0)
        users: List[TelegramUser] = await asyncio.to_thread(list, users_qs)
    except Exception:
        logger.exception("Ошибка получения пользователей с непрочитанными молниями")
        await _safe_close_bot(bot)
        return {
            "total_messages_sent": 0,
            "total_errors": 0,
        }

    # Первая попытка отправки
    failed_users: List[int] = []
    for i in range(0, len(users), batch_size):
        batch_users = users[i : i + batch_size]
        for user in batch_users:
            try:
                # Получаем непрочитанные молнии с полной фильтрацией, как в кнопке
                unread_lightnings = await list_unread_lightnings(user.id, since=None)
                if not unread_lightnings:
                    continue

                # GIF перед текстом (если включено и файл есть)
                if enable_gif and gif_path:
                    try:
                        await bot.send_animation(
                            chat_id=user.telegram_id,
                            animation=FSInputFile(gif_path),
                        )
                        total_messages_sent += 1
                    except TelegramBadRequest:
                        logger.warning(
                            "GIF: чат не найден для пользователя %s", user.telegram_id
                        )
                    except Exception:
                        logger.warning(
                            "GIF: не удалось отправить пользователю %s",
                            user.telegram_id,
                        )

                ids = [l.id for l in unread_lightnings]
                status = await get_lightnings_status(user.id, ids) if ids else {}
                kb = get_lightnings_list_kb(unread_lightnings, status=status)
                text = "Вам поступили новые молнии. Ознакомьтесь, нажав на соответствующую кнопку:"
                await bot.send_message(user.telegram_id, text, reply_markup=kb)
                total_messages_sent += 1

                await asyncio.sleep(delay_between_users)
            except TelegramRetryAfter as e:
                await asyncio.sleep(getattr(e, "retry_after", 1))
                total_errors += 1
                failed_users.append(user.id)
            except TelegramForbiddenError:
                total_errors += 1
            except TelegramBadRequest:
                logger.warning(
                    "MSG: чат не найден для пользователя %s", user.telegram_id
                )
                total_errors += 1
            except TelegramNetworkError:
                total_errors += 1
            except Exception:
                logger.exception(
                    "Ошибка отправки сообщения пользователю %s", user.telegram_id
                )
                total_errors += 1

        # Пауза между батчами (если это не последний пакет)
        if i + batch_size < len(users):
            await asyncio.sleep(delay_between_batches)

    # Повторные попытки для пользователей с ошибками
    attempt = 2
    while failed_users and attempt <= max_retry_attempts:
        # Экспоненциальная пауза, но не более 30 секунд
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
                    unread_lightnings = await list_unread_lightnings(
                        user.id, since=None
                    )
                    if not unread_lightnings:
                        continue

                    if enable_gif and gif_path:
                        try:
                            await bot.send_animation(
                                chat_id=user.telegram_id,
                                animation=FSInputFile(gif_path),
                            )
                            total_messages_sent += 1
                        except TelegramBadRequest:
                            logger.warning(
                                "GIF: чат не найден для пользователя %s",
                                user.telegram_id,
                            )
                        except Exception:
                            logger.warning(
                                "GIF: не удалось отправить пользователю %s",
                                user.telegram_id,
                            )

                    ids = [l.id for l in unread_lightnings]
                    status = await get_lightnings_status(user.id, ids) if ids else {}
                    kb = get_lightnings_list_kb(unread_lightnings, status=status)
                    text = "Вам поступили новые молнии. Ознакомьтесь, нажав на соответствующую кнопку:"
                    await bot.send_message(user.telegram_id, text, reply_markup=kb)
                    total_messages_sent += 1
                    await asyncio.sleep(delay_between_users)
                except TelegramRetryAfter as e:
                    await asyncio.sleep(getattr(e, "retry_after", 1))
                    total_errors += 1
                    still_failed.append(user.id)
                except TelegramForbiddenError:
                    total_errors += 1
                except TelegramBadRequest:
                    logger.warning(
                        "MSG: чат не найден для пользователя %s", user.telegram_id
                    )
                    total_errors += 1
                except TelegramNetworkError:
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
