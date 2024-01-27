from django.core.management import BaseCommand  # Импорт класса BaseCommand из Django для создания собственных команд.
import logging  # Импорт модуля для логирования.
from icecream import ic  # Импорт библиотеки icecream для более удобного вывода отладочной информации.
import asyncio  # Импорт модуля asyncio для асинхронного программирования.
from aiogram import Bot, Dispatcher
from .handlers import start_menu, exception, main_menu
from .middleware import user_logic 
''''''
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters.command import Command
''''''
logging.basicConfig(level=logging.INFO)  # Настройка логирования для вывода информационных сообщений.

BOT_TOKEN = '6686307025:AAFz1tjuBXs3_4m6eAUBII2B5I5j3GPj4uE'

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    #dp.update.middleware(user_logic.UserLanguageMiddleware())

    #Роутеры (группы обработчиков) для начального меню, основного меню и обработки исключений регистрируются в диспетчере. 
    #Это организует логику обработки сообщений в зависимости от их типа и содержания.
    dp.include_routers(start_menu.router, main_menu.router, exception.router)

    #Запускаем бота в режиме опроса. Получаем и обрабатываем сообщения от пользователя
    await dp.start_polling(bot)


#Класс Command наследует от BaseCommand Django, что позволяет создать собственную команду управления, которую можно запустить через manage.py
class Command(BaseCommand):
    help = 'Telegram bot start!'

    def handle(self, *args, **options):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )

        #выводит описание команды
        ic(self.help)

        #запускает асинхронную функцию main (где работает бот) и выводит результаты ее выполнения
        ic(asyncio.run(main()))



# if __name__ == "__main__":
#     asyncio.run(main())