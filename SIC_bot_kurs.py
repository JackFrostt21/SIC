from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import logging

# Определяем состояние разговора
FIO = 0

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен, который вы получили от BotFather
TOKEN = "6686307025:AAFz1tjuBXs3_4m6eAUBII2B5I5j3GPj4uE"

# Список курсов
courses = ["Курс 1", "Курс 2", "Курс 3"]

# Хранилище данных о пользователях и их выборах
user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отправляет приветственное сообщение и запрашивает ФИО"""
    await update.message.reply_text(
        "Привет! Я бот для выбора курсов. Пожалуйста, введите ваше ФИО."
    )
    return FIO


async def fio_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет ФИО пользователя и завершает разговор"""
    user_fio = update.message.text
    user_id = update.message.from_user.id
    user_data[user_id] = {"fio": user_fio, "course": None}
    await update.message.reply_text(
        f"Спасибо, {user_fio}! Теперь вы можете выбрать курс, используя команду /courses."
    )
    return ConversationHandler.END


async def courses_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает список курсов"""
    keyboard = [
        [InlineKeyboardButton(course, callback_data=course)] for course in courses
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Пожалуйста, выберите курс:", reply_markup=reply_markup
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатия на кнопки"""
    query = update.callback_query
    await query.answer()
    selected_course = query.data
    user_id = query.from_user.id

    # Проверяем, есть ли уже информация о пользователе в user_data
    if user_id in user_data:
        # Обновляем информацию о выбранном курсе
        user_data[user_id]["course"] = selected_course
    else:
        # Если информации о пользователе нет, создаем новую запись
        user_data[user_id] = {"fio": "Неизвестно", "course": selected_course}

    await query.edit_message_text(text=f"Вы выбрали: {selected_course}")


async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет информацию о выборе пользователя"""
    user_id = update.message.from_user.id
    if user_id in user_data:
        await update.message.reply_text(f"Вы выбрали курс: {user_data[user_id]}")
    else:
        await update.message.reply_text("Вы еще не выбрали курс.")


async def admin_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет информацию о всех пользователях и их выборах."""
    info = []
    for user_info in user_data.values():
        if "fio" in user_info and "course" in user_info and user_info["course"]:
            info.append(f'Сотрудник {user_info["fio"]}: выбрал {user_info["course"]}')
    info_str = "\n".join(info)
    await update.message.reply_text(
        info_str if info_str else "Нет данных о пользователях."
    )


def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, fio_received)]},
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("courses", courses_list))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("getinfo", get_info))
    application.add_handler(CommandHandler("admininfo", admin_info))

    application.run_polling()


if __name__ == "__main__":
    main()
