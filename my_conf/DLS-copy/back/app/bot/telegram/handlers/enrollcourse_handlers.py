from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

from app.learning_app.services.course_content_service import CourseContentService

router = Router(name="enrollcourse_router")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


@router.message(F.text == "✏️ Самозапись на курсы")
async def process_booking_message(
    message: Message, state: FSMContext, course_content_service: CourseContentService
) -> None:
    """
    Обработчик кнопки самозаписи.
    Получает список открытых курсов и показывает их пользователю.
    """
    telegram_id = message.from_user.id

    # Запрашиваем открытые курсы у сервиса
    result = await course_content_service.get_open_courses(telegram_id)

    if not result["success"]:
        await message.answer(
            result.get("message", "Ошибка при получении списка курсов.")
        )
        return

    courses = result["courses"]

    if not courses:
        await message.answer(
            "В настоящий момент нет доступных открытых курсов для записи."
        )
        return

    # Формируем клавиатуру со списком курсов
    builder = InlineKeyboardBuilder()
    for course in courses:
        # Создаем кнопку: Название курса -> callback с ID курса
        # Префикс 'enroll:' используется для отлова нажатия в следующем хендлере
        builder.button(text=f"📖 {course.title}", callback_data=f"enroll:{course.id}")
    builder.adjust(1)  # По 1 кнопке в ряду

    keyboard = builder.as_markup()

    await message.answer(
        "<b>✏️ Доступные курсы для записи:</b>\n\nВыберите курс, чтобы записаться:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("enroll:"))
async def process_course_enrollment(
    callback: CallbackQuery, course_content_service: CourseContentService
) -> None:
    """
    Обработчик нажатия на кнопку записи.
    """
    # Парсим ID курса из callback_data (формат 'enroll:123')
    try:
        course_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный идентификатор курса.", show_alert=True)
        return

    telegram_id = callback.from_user.id

    # Вызываем сервис для записи
    result = await course_content_service.enroll_in_course(telegram_id, course_id)

    if result["success"]:
        # Уведомляем пользователя об успехе и удаляем клавиатуру/сообщение или обновляем его
        await callback.answer("Вы успешно записаны!", show_alert=True)
        await callback.message.edit_text(
            "✅ <b>Поздравляем! Вы успешно записались на курс.</b>\n\n"
            'Теперь он доступен в разделе "📚 Программы обучения".',
            parse_mode="HTML",
        )
    else:
        # Если ошибка (например, уже записан или курс закрыт)
        error_msg = result.get("message", "Не удалось записаться на курс.")
        await callback.answer(error_msg, show_alert=True)
