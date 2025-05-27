import logging
import asyncio
from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from django.conf import settings


# Сервисы и хэндлеры
from app.bot.services.telegram_user_service import TelegramUserService

# from app.bot.handlers.commands import register_command_handlers
# from app.bot.handlers.callbacks import register_callback_handlers
# from app.bot.handlers.messages import register_message_handlers

# Импорт роутеров
from app.bot.telegram.handlers.start import router as start_router
from app.bot.telegram.handlers.main_menu import router as main_menu_router
from app.bot.telegram.handlers.testing_handlers import testing_router

# Импорт middleware для инъекции зависимостей
from app.bot.telegram.middlewares.dependencies import DependencyInjectMiddleware


# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запуск Telegram бота"

    def handle(self, *args, **options):
        # Запускаем бота в асинхронном режиме
        asyncio.run(self.start_bot())

    async def start_bot(self):
        # Инициализация Telegram Bot с HTML парсингом
        default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=default_properties)

        # Хранилище состояний FSM
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Регистрация мидлвари
        dp.update.middleware.register(DependencyInjectMiddleware())

        # Регистрация роутеров
        dp.include_router(start_router)  # Регистрируем роутер команды start
        dp.include_router(main_menu_router)  # Регистрируем роутер главного меню
        dp.include_router(testing_router)  # Регистрируем роутер тестирования

        # Регистрация дополнительных хэндлеров
        # TODO: добавить хэндлеры
        # register_command_handlers(dp)
        # register_callback_handlers(dp)
        # register_message_handlers(dp)

        # Очистка накопленных апдейтов
        await bot.delete_webhook(drop_pending_updates=True)

        self.stdout.write(self.style.SUCCESS("Бот запущен!"))

        # Запуск поллинга
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
        finally:
            await bot.session.close()
