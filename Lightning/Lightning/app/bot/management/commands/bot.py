import asyncio
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.telegram.routers import build_router
from app.core.middlewares.bot_activity import ActivityLogMiddleware


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запуск Telegram бота Молния"

    def handle(self, *args, **options):
        # Запускаем бота в асинхронном режиме
        try:
            asyncio.run(self.start_bot())
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при работе бота: {e}", exc_info=True)

    async def start_bot(self):
        # Инициализация бота (HTML по умолчанию)
        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        # Хранилище состояний FSM
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Регистрация мидлварей:
        # 1) ActivityLogMiddleware — логирование входящих событий и обновление last_activity
        dp.update.middleware(ActivityLogMiddleware())

        # Роутеры TODO:
        dp.include_router(build_router())

        # Очистка накопленных апдейтов
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот запущен!")

        # Запуск поллинга
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except asyncio.CancelledError:
            logger.info("Поллинг остановлен (CancelledError)")
        except KeyboardInterrupt:
            logger.info("Поллинг остановлен пользователем (KeyboardInterrupt)")
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        finally:
            # Корректный shutdown
            try:
                if hasattr(dp.storage, "close"):
                    await dp.storage.close()
                if hasattr(dp.storage, "wait_closed"):
                    await dp.storage.wait_closed()
            except Exception:
                pass
            await bot.session.close()
            logger.info("Бот остановлен")
