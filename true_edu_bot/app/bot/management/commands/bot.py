from aiogram.utils import executor
from django.core.management import BaseCommand
import logging
from app.bot.management.commands.loader import dp
from icecream import ic
from . import bot_logic

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Telegram bot'

    def handle(self, *args, **options):
        ic(bot_logic)
        # Подключение
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        ic(f'Бот стартовал!')
        ic(executor.start_polling(dp, skip_updates=False))
