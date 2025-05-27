from typing import Dict, Any, List, Optional
from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    Message,
    InlineKeyboardButton,
    WebAppInfo,
)
from aiogram.fsm.context import FSMContext
import os
import logging

from app.bot.telegram.deps import UserService
from app.learning_app.repositories import CourseRepository
from app.learning_app.services.course_content_service import CourseContentService
from app.bot.telegram.keyboards.builders import InlineKeyboardBuilder
from app.bot.telegram.utils.text_formatters import (
    clean_html_for_telegram,
    paginate_text,
)
from app.organization.repositories import SettingsBotRepository
from aiogram.filters import Command
from app.bot.telegram.callback.schemas import CourseMenuCallback

# Создаем роутер для обработчиков главного меню
router = Router(name="main_menu_router")


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализируем репозитории
course_repo = CourseRepository()
settings_repo = SettingsBotRepository()


async def _send_courses_list(
    telegram_id: int,
    course_content_service: CourseContentService,
    message_sender,  # Может быть message или callback.message
    add_back_button: bool = False,
) -> None:
    """
    Вспомогательная функция для отправки списка курсов.
    Устраняет дублирование кода между обработчиками сообщений и callback'ов.
    """
    logger.info(f"Sending courses list for telegram_id: {telegram_id}")

    # Получаем список доступных курсов со статусами тестов
    logger.info("Fetching available courses...")
    courses_data = await course_content_service.course_repository.get_available_courses(
        telegram_id
    )
    logger.info(f"Courses data received: {courses_data}")

    # Получаем изображение для списка курсов
    logger.info("Fetching list courses image path...")
    list_courses_image_path = await settings_repo.get_list_courses_image_path()
    logger.info(f"List courses image path: {list_courses_image_path}")

    if not courses_data:
        logger.info("No courses data found.")
        # Если курсов нет, отправляем сообщение об этом
        no_courses_text = (
            "<b>📚 Программы обучения</b>\n\n"
            "В настоящий момент для вас нет доступных программ обучения.\n"
            "Пожалуйста, обратитесь к администратору для получения доступа."
        )

        if list_courses_image_path and os.path.exists(list_courses_image_path):
            logger.info(
                f"Image path exists: {list_courses_image_path}. Sending photo with no courses message."
            )
            await message_sender.answer_photo(
                photo=FSInputFile(list_courses_image_path),
                caption=no_courses_text,
            )
        else:
            logger.info(
                "Image path does not exist or not provided. Sending text message with no courses."
            )
            await message_sender.answer(no_courses_text)
    else:
        # Формируем список курсов с кнопками
        logger.info(f"Courses data found: {len(courses_data)} courses.")
        courses_text = "<b>📚 Доступные программы обучения:</b>\n\n"
        buttons = []

        for item in courses_data:
            course = item["course"]
            test_status = item["test_status"]
            test_score = item["test_score"]

            prefix = ""
            if test_status == "completed_passed":
                prefix = f"✔️ "
            elif test_status == "completed_failed":
                prefix = f"❌ "

            course_title = f"{prefix}{course.title}"
            if test_score is not None:
                course_title += f" ({test_score}%)"

            # # Добавляем информацию о курсе в текст
            # courses_text += f"<b>{course_title}</b>\n"
            # courses_text += (
            #     f"{course.description[:100]}...\n\n" if course.description else "\n"
            # )

            # Добавляем кнопку для курса
            buttons.append([(f"📖 {course_title}", f"course:{course.id}")])

        # # Добавляем кнопку возврата в главное меню
        # buttons.append([("🔙 Назад", "back_to_main_menu")])

        # Создаем инлайн-клавиатуру для выбора курса
        courses_keyboard = InlineKeyboardBuilder.create_inline_kb(buttons)

        # Отправляем сообщение со списком курсов
        if list_courses_image_path and os.path.exists(list_courses_image_path):
            logger.info(
                f"Image path exists: {list_courses_image_path}. Sending photo with courses list."
            )
            await message_sender.answer_photo(
                photo=FSInputFile(list_courses_image_path),
                caption=courses_text,
                reply_markup=courses_keyboard,
            )
        else:
            logger.info(
                "Image path does not exist or not provided. Sending text message with courses list."
            )
            await message_sender.answer(courses_text, reply_markup=courses_keyboard)


@router.message(F.text == "📚 Программы обучения")
@router.message(Command("courses"))
async def process_courses_message(
    message: Message,
    state: FSMContext,
    user_service: UserService,
    course_content_service: CourseContentService,
) -> None:
    """
    Обрабатывает нажатие на кнопку "Программы обучения" из обычной клавиатуры
    Отображает список доступных курсов
    """
    logger.info("Entering process_courses_message handler")

    telegram_id = message.from_user.id
    logger.info(f"Telegram ID: {telegram_id}")

    await _send_courses_list(
        telegram_id=telegram_id,
        course_content_service=course_content_service,
        message_sender=message,
        add_back_button=False,
    )


@router.callback_query(F.data == "courses_list")
async def process_courses_button(
    callback: CallbackQuery,
    state: FSMContext,
    user_service: UserService,
    course_content_service: CourseContentService,
) -> None:
    """
    Обрабатывает нажатие на кнопку "Программы обучения" через callback
    Отображает список доступных курсов
    """
    logger.info("Entering process_courses_button handler")
    await callback.answer()

    telegram_id = callback.from_user.id
    logger.info(f"Telegram ID: {telegram_id}")

    # Сначала удалим старое сообщение
    try:
        await callback.message.delete()
        logger.info("Previous message deleted successfully.")
    except Exception as e:
        logger.error(f"Error deleting previous message: {e}")

    await _send_courses_list(
        telegram_id=telegram_id,
        course_content_service=course_content_service,
        message_sender=callback.message,
        add_back_button=True,
    )


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery) -> None:
    """
    Обрабатывает возврат в главное меню
    """
    # Импортируем здесь, чтобы избежать циклических импортов
    from app.bot.telegram.keyboards.main_kb import get_main_menu_keyboard

    # Получаем главную клавиатуру
    main_menu_keyboard = await get_main_menu_keyboard(callback.from_user.id)

    # TODO: убрал кнопку назад, посмотреть блок, нужен или нет
    # Отправляем новое сообщение с главной клавиатурой
    await callback.message.answer(
        "<b>🏠 Главное меню</b>\n\n" "Выберите раздел для продолжения работы с ботом:",
        reply_markup=main_menu_keyboard,
    )

    await callback.answer()


@router.callback_query(F.data.startswith("course:"))
async def process_course_selection(
    callback: CallbackQuery, course_content_service: CourseContentService
) -> None:
    """
    Обрабатывает выбор курса и отображает список тем данного курса
    """
    logger.info(f"Entering process_course_selection for callback: {callback.data}")
    await callback.answer()
    telegram_id = callback.from_user.id
    # Извлекаем ID курса из callback_data
    try:
        course_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        logger.error(f"Invalid course_id in callback data: {callback.data}")
        await callback.answer("Некорректный идентификатор курса.", show_alert=True)
        return

    logger.info(
        f"Fetching course content for course_id: {course_id}, telegram_id: {telegram_id}"
    )
    result = await course_content_service.get_course_content(telegram_id, course_id)

    if not result["success"]:
        logger.warning(
            f"Failed to get course content for course_id: {course_id}. Message: {result.get('message')}"
        )
        await callback.answer(result.get("message", "Курс не найден."), show_alert=True)
        return

    course = result["course"]
    topics = result["topics"]
    logger.info(
        f"Course content received: {course['title']}, Topics count: {len(topics)}"
    )

    # Формируем текст сообщения с описанием курса и списком тем
    message_text = f"<b>📖 {course['title']}</b>\n"
    if course["description"]:
        message_text += f"{course['description']}\n"
    message_text += "\nСписок тем:\n"

    buttons = []
    for topic in topics:
        title = topic["title"]
        if topic["is_read"]:
            title = f"✔️ {title}"
        # CallbackData для выбора темы
        cb_data = CourseMenuCallback(
            action="topic", course_id=course_id, topic_id=topic["id"], page=1
        ).pack()
        buttons.append([(title, cb_data)])
    # Добавляем кнопку назад к списку курсов
    buttons.append([("🔙 Назад к списку курсов", "courses_list")])

    # Добавляем кнопку Тестирования
    test_status = course.get("test_status")
    test_score = course.get("test_score")
    test_button_text = "📝 Начать тестирование"
    test_callback_data = f"test_action:start:{course['id']}"

    if test_status == "completed_passed":
        test_button_text = f"✔️ Тест сдан ({test_score}%)"
        test_callback_data = (
            f"test_action:show_results:{course['id']}"  # Показать результаты
        )
    elif test_status == "completed_failed":
        test_button_text = f"❌ Тест не сдан ({test_score}%) - Повторить"
        test_callback_data = (
            f"test_action:start:{course['id']}"  # Начать заново/повторить
        )

    buttons.append([(test_button_text, test_callback_data)])

    keyboard = InlineKeyboardBuilder.create_inline_kb(buttons)

    # Удаляем предыдущее сообщение
    try:
        await callback.message.delete()
        logger.info("Previous message deleted in process_course_selection.")
    except Exception as e:
        logger.error(f"Error deleting message in process_course_selection: {e}")

    await callback.message.answer(text=message_text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(CourseMenuCallback.filter(F.action == "topic"))
async def process_topic_selection(
    callback: CallbackQuery,
    callback_data: CourseMenuCallback,
    bot: Bot,
    course_content_service: CourseContentService,
) -> None:
    """
    Обрабатывает выбор темы и отображает ее содержимое.
    """
    logger.info(f"Entering process_topic_selection for callback: {callback.data}")
    await callback.answer()
    if callback_data.action != "topic":
        return
    # Параметры из callback_data
    course_id = callback_data.course_id
    topic_id = callback_data.topic_id
    page = callback_data.page
    logger.info(
        f"Processing topic selection: course_id={course_id}, topic_id={topic_id}, page={page}"
    )

    telegram_id = callback.from_user.id
    result = await course_content_service.get_topic_content(
        telegram_id, course_id, topic_id
    )

    if not result["success"]:
        logger.warning(
            f"Failed to get topic content for topic_id: {topic_id}. Message: {result.get('message')}"
        )
        await callback.answer(
            result.get("message", "Тема не найдена или недоступна."), show_alert=True
        )
        return

    content = result["content"]

    # Формируем текст сообщения с описанием темы (текст темы доступен по отдельной кнопке)
    caption_text = f"<b>📌 {content['title']}</b>\n"
    if content["description"]:
        caption_text += f"<i>{content['description']}</i>\n\n"
    else:
        caption_text += "\n"

    # Сборка кнопок: сначала кнопка просмотра текста
    buttons = []
    if content["main_text_readuser"] and content["text_content"]:
        text_cb = CourseMenuCallback(
            action="content_text", course_id=course_id, topic_id=topic_id, page=1
        ).pack()
        buttons.append([("📖 Текст", text_cb)])

    # Кнопки для контента (PDF, Audio, Video)
    if content["has_pdf"]:
        buttons.append([("📄 PDF", f"content_type:{course_id}:{topic_id}:pdf")])
    if content["has_audio"]:
        buttons.append([("🎵 Аудио", f"content_type:{course_id}:{topic_id}:audio")])
    if content["has_video"]:
        buttons.append([("▶️ Видео", f"content_type:{course_id}:{topic_id}:video")])
    if content["main_text_webapp_readuser"]:
        base_url_for_webapp = (
            await settings_repo.get_url_web_app()
        )  # Получаем из настроек
        if base_url_for_webapp:
            # Убираем возможный слеш в конце из настроек, чтобы избежать двойного слеша
            base_url_for_webapp = base_url_for_webapp.rstrip("/")
            webapp_topic_url = f"{base_url_for_webapp}/webapp/topic/{topic_id}/text/"
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="🌐 Открыть текст в WebApp",
                        web_app=WebAppInfo(url=webapp_topic_url),
                    )
                ]
            )
        else:
            logger.warning("Base URL for WebApp is not set in bot settings.")

    # Кнопка назад к списку тем курса
    back_cb = CourseMenuCallback(action="list_topics", course_id=course_id).pack()
    buttons.append([("🔙 Назад к темам", back_cb)])

    keyboard = InlineKeyboardBuilder.create_inline_kb(buttons)

    # Удаляем предыдущее сообщение, чтобы корректно обновить (фото/текст)
    await callback.message.delete()

    if content.get("image_path") and os.path.exists(content["image_path"]):
        photo = FSInputFile(content["image_path"])
        await callback.message.answer_photo(
            photo=photo,
            caption=caption_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    else:
        await callback.message.answer(
            text=caption_text,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    await callback.answer()


@router.callback_query(F.data.startswith("content_type:"))
async def process_content_type_selection(
    callback: CallbackQuery, course_content_service: CourseContentService
) -> None:
    """
    Обрабатывает запрос на получение контента определенного типа (PDF, аудио, видео).
    """
    logger.info(
        f"Entering process_content_type_selection for callback: {callback.data}"
    )
    await callback.answer()
    parts = callback.data.split(":")
    try:
        telegram_id = callback.from_user.id
        course_id = int(parts[1])
        topic_id = int(parts[2])
        content_key = parts[3]  # 'pdf', 'audio', 'video'
        logger.info(
            f"Processing content type: course_id={course_id}, topic_id={topic_id}, content_key='{content_key}'"
        )
    except (IndexError, ValueError):
        logger.error(f"Invalid data in content_type callback: {callback.data}")
        await callback.answer(
            "Ошибка в данных для получения контента.", show_alert=True
        )
        return

    result = None

    if content_key == "pdf":
        logger.info(f"Fetching PDF for course {course_id}, topic {topic_id}")
        result = await course_content_service.get_pdf_file(
            telegram_id, course_id, topic_id
        )
    elif content_key == "audio":
        logger.info(f"Fetching audio for course {course_id}, topic {topic_id}")
        result = await course_content_service.get_audio_file(
            telegram_id, course_id, topic_id
        )
    elif content_key == "video":
        logger.info(f"Fetching video for course {course_id}, topic {topic_id}")
        result = await course_content_service.get_video_file(
            telegram_id, course_id, topic_id
        )
    else:
        logger.warning(f"Unknown content type: {content_key}")
        await callback.answer("Неизвестный тип контента.", show_alert=True)
        return

    if result and result["success"]:
        file_info = result["file_info"]
        file_path = file_info["path"]
        file_title = file_info["title"]
        logger.info(f"File found: {file_path}, title: {file_title}")
        input_file = FSInputFile(file_path)
        try:
            if content_key == "pdf":
                await callback.message.answer_document(
                    input_file, caption=f"📄 {file_title}"
                )
            elif content_key == "audio":
                await callback.message.answer_audio(
                    input_file, caption=f"🎵 {file_title}"
                )
            elif content_key == "video":
                await callback.message.answer_video(
                    input_file, caption=f"▶️ {file_title}"
                )
            logger.info(f"Successfully sent {content_key} file: {file_path}")
            await callback.answer()  # Отвечаем на коллбэк после успешной отправки файла
        except Exception as e:
            logger.error(f"Failed to send file {file_path}: {e}")
            await callback.answer(f"Не удалось отправить файл: {e}", show_alert=True)
    else:
        error_message = (
            result.get("message", "Файл не найден или недоступен.")
            if result
            else "Произошла ошибка при получении файла."
        )
        logger.warning(f"Failed to get file: {error_message}")
        await callback.answer(error_message, show_alert=True)


@router.callback_query(CourseMenuCallback.filter(F.action == "content_text"))
async def process_content_text(
    callback: CallbackQuery,
    callback_data: CourseMenuCallback,
    course_content_service: CourseContentService,
) -> None:
    """
    Отображает текст темы постранично по отдельному запросу.
    """
    await callback.answer()
    if callback_data.action != "content_text":
        return
    # Параметры из callback_data
    course_id = callback_data.course_id
    topic_id = callback_data.topic_id
    page_num = callback_data.page
    # Получаем содержимое темы
    result = await course_content_service.get_topic_content(
        callback.from_user.id, course_id, topic_id
    )
    if not result.get("success"):
        await callback.answer(
            result.get("message", "Ошибка получения темы"), show_alert=True
        )
        return
    content = result["content"]
    if not content.get("main_text_readuser") or not content.get("text_content"):
        await callback.answer("Текст темы недоступен.", show_alert=True)
        return
    cleaned = clean_html_for_telegram(content["text_content"])
    text_page, current_page, total_pages = paginate_text(cleaned, page_number=page_num)
    # Навигационные кнопки
    nav = []
    if current_page > 1:
        prev_cb = CourseMenuCallback(
            action="content_text",
            course_id=course_id,
            topic_id=topic_id,
            page=current_page - 1,
        ).pack()
        nav.append(("⬅️ Пред.", prev_cb))
    nav.append((f"Стр. {current_page}/{total_pages}", "noop"))
    if current_page < total_pages:
        next_cb = CourseMenuCallback(
            action="content_text",
            course_id=course_id,
            topic_id=topic_id,
            page=current_page + 1,
        ).pack()
        nav.append(("След. ➡️", next_cb))
    buttons = []
    if nav:
        buttons.append(nav)
    # Кнопка назад к содержанию темы
    topic_cb = CourseMenuCallback(
        action="topic", course_id=course_id, topic_id=topic_id, page=page_num
    ).pack()
    buttons.append([("🔙 Назад к теме", topic_cb)])
    keyboard = InlineKeyboardBuilder.create_inline_kb(buttons)
    # Редактируем сообщение с текстом темы
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Error deleting message before sending text page: {e}")
    await callback.message.answer(
        text_page,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.callback_query(CourseMenuCallback.filter(F.action == "list_topics"))
async def process_list_topics(
    callback: CallbackQuery,
    callback_data: CourseMenuCallback,
    course_content_service: CourseContentService,
) -> None:
    """
    Обрабатывает возврат к списку тем курса.
    """
    await callback.answer()
    telegram_id = callback.from_user.id
    course_id = callback_data.course_id
    result = await course_content_service.get_course_content(telegram_id, course_id)
    if not result["success"]:
        await callback.answer(
            result.get("message", "Не удалось получить список тем."), show_alert=True
        )
        return

    course = result["course"]
    topics = result["topics"]

    message_text = f"<b>📖 {course['title']}</b>\n"
    if course["description"]:
        message_text += f"{course['description']}\n"
    message_text += "\nСписок тем:\n"

    buttons = []
    for topic in topics:
        title = topic["title"]
        if topic["is_read"]:
            title = f"✔️ {title}"
        cb_data = CourseMenuCallback(
            action="topic", course_id=course_id, topic_id=topic["id"], page=1
        ).pack()
        buttons.append([(title, cb_data)])

    buttons.append([("🔙 Назад к списку курсов", "courses_list")])

    keyboard = InlineKeyboardBuilder.create_inline_kb(buttons)

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(text=message_text, reply_markup=keyboard)
    await callback.answer()
