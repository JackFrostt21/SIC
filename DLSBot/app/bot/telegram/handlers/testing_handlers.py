from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

from app.learning_app.services.test_service import TestService

from app.bot.telegram.keyboards.test_kb import (
    build_question_keyboard,
    CB_TEST_ACTION_FINISH,
    CB_TEST_ANSWER_SELECT,
    CB_TEST_QUESTION_NEXT,
)
from app.bot.telegram.states.test_state import TestState
from app.bot.telegram.utils.text_formatters import clean_html_for_telegram

testing_router = Router(name=__name__)


@testing_router.callback_query(F.data.startswith("test_action:start:"))
async def process_start_test(
    callback: CallbackQuery, state: FSMContext, bot: Bot, test_service: TestService
):
    """
    Обработчик нажатия кнопки "Начать тест" или "Повторить тест".
    Запускает новый тест или перезапускает существующий (если пользователь был в процессе).
    """
    await callback.answer()
    _, _, course_id_str = callback.data.split(":")
    course_id = int(course_id_str)

    current_state = await state.get_state()
    if current_state == TestState.in_progress:
        await state.clear()  # Очищаем предыдущее состояние, если было

    initial_test_data = await test_service.start_test_attempt(
        telegram_id=callback.from_user.id, course_id=course_id
    )

    if not initial_test_data.get("success"):
        try:
            await callback.message.edit_text(
                initial_test_data.get("message", "Не удалось начать тест.")
            )
        except AttributeError:  # Если callback.message None или не имеет edit_text
            await callback.message.answer(
                initial_test_data.get("message", "Не удалось начать тест.")
            )
        return

    question_data = initial_test_data.get("question")
    if not question_data:
        try:
            await callback.message.edit_text("В тесте нет вопросов.")
        except AttributeError:
            await callback.message.answer("В тесте нет вопросов.")
        return

    all_q_ids = initial_test_data.get("all_questions_ids", [])
    current_q_idx = initial_test_data.get("current_question_index")
    total_questions = initial_test_data.get("total_questions")

    message_text = f"<b>Тест по курсу: {initial_test_data.get('course_title')}</b>\n\n"
    message_text += f"Вопрос {question_data['order']}/{total_questions}:\n"
    message_text += clean_html_for_telegram(question_data["text"])

    keyboard = build_question_keyboard(
        question_id=question_data["id"],
        options=question_data["options"],
        is_multiple_choice=question_data["is_multiple_choice"],
        course_id=course_id,
        all_questions_ids_str=",".join(map(str, all_q_ids)),
        current_question_index=current_q_idx,
        total_questions=total_questions,
        selected_answers_ids=set(),  # Для первого вопроса выбранных ответов нет
    )

    sent_message = await callback.message.answer(
        message_text, reply_markup=keyboard.as_markup()
    )

    # Устанавливаем состояние и сохраняем данные теста
    await state.set_state(TestState.in_progress)
    await state.update_data(
        course_id=course_id,
        course_title=initial_test_data.get("course_title"),
        all_questions_ids=all_q_ids,
        current_question_index=current_q_idx,
        user_answers={},
        total_questions=total_questions,
        message_id_to_edit=sent_message.message_id,
        chat_id=callback.message.chat.id,  # chat_id для редактирования сообщения
        current_question_details=question_data,
    )


@testing_router.callback_query(
    F.data.startswith(CB_TEST_ANSWER_SELECT) & TestState.in_progress
)
async def process_select_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обрабатывает выбор/снятие выбора ответа на вопрос.
    Обновляет клавиатуру сообщения с вопросом.
    """
    await callback.answer()  # Сразу отвечаем на callback, чтобы кнопка не "зависала"

    parts = callback.data.split(":")
    try:
        question_id_from_cb = int(parts[5])
        selected_option_id = int(parts[6])
        is_multiple_choice_from_cb = bool(int(parts[7]))
    except (IndexError, ValueError) as e:
        print(f"Error parsing select_answer callback data: {callback.data}, error: {e}")
        return

    fsm_data = await state.get_data()
    user_answers: dict = fsm_data.get("user_answers", {})
    current_question_details: dict = fsm_data.get("current_question_details")
    message_id_to_edit = fsm_data.get("message_id_to_edit")
    chat_id = fsm_data.get("chat_id")

    if (
        not current_question_details
        or current_question_details.get("id") != question_id_from_cb
    ):
        print(
            f"Mismatch in question ID. FSM: {current_question_details.get('id') if current_question_details else 'None'}, CB: {question_id_from_cb}"
        )
        return

    # Обновляем user_answers
    current_answers_for_question = set(user_answers.get(question_id_from_cb, []))

    if is_multiple_choice_from_cb:
        if selected_option_id in current_answers_for_question:
            current_answers_for_question.remove(selected_option_id)
        else:
            current_answers_for_question.add(selected_option_id)
    else:  # Одиночный выбор
        if (
            selected_option_id in current_answers_for_question
        ):  # Повторное нажатие на выбранный = снять выбор
            current_answers_for_question.clear()
        else:
            current_answers_for_question = {selected_option_id}

    user_answers[question_id_from_cb] = list(current_answers_for_question)
    await state.update_data(user_answers=user_answers)

    # Обновляем клавиатуру
    # Данные для клавиатуры берем из FSM, где хранится состояние текущего вопроса
    keyboard = build_question_keyboard(
        question_id=current_question_details["id"],
        options=current_question_details["options"],
        is_multiple_choice=current_question_details["is_multiple_choice"],
        course_id=fsm_data["course_id"],
        all_questions_ids_str=",".join(map(str, fsm_data["all_questions_ids"])),
        current_question_index=fsm_data["current_question_index"],
        total_questions=fsm_data["total_questions"],
        selected_answers_ids=current_answers_for_question,  # Передаем обновленные выбранные ответы
    )

    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=keyboard.as_markup(),
        )
    except Exception as e:
        print(f"Error editing message reply markup: {e}")


@testing_router.callback_query(
    F.data.startswith(CB_TEST_QUESTION_NEXT) & TestState.in_progress
)
async def process_next_question(
    callback: CallbackQuery, state: FSMContext, bot: Bot, test_service: TestService
):
    """
    Обрабатывает нажатие кнопки "Далее" для перехода к следующему вопросу.
    """
    await callback.answer()

    fsm_data = await state.get_data()
    course_id = fsm_data["course_id"]
    course_title = fsm_data["course_title"]
    all_questions_ids = fsm_data["all_questions_ids"]
    current_question_index = fsm_data["current_question_index"]
    total_questions = fsm_data["total_questions"]
    message_id_to_edit = fsm_data["message_id_to_edit"]
    chat_id = fsm_data["chat_id"]
    # TODO: user_answers = fsm_data["user_answers"] # Ответы на текущий вопрос уже должны быть сохранены process_select_answer

    # Проверка, что это не последний вопрос (хотя клавиатура не должна давать нажать "Далее" на последнем)
    if current_question_index >= total_questions - 1:
        # Этого не должно происходить, если логика клавиатуры верна
        await bot.edit_message_text(
            text="Это был последний вопрос. Нажмите 'Завершить тест'.",
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=None,  # TODO: Убрать старую клавиатуру или показать кнопку Завершить?
        )
        return

    next_question_data_result = await test_service.get_next_question_data(
        course_id=course_id,  # course_id нужен сервису?
        all_questions_ids=all_questions_ids,
        current_question_index=current_question_index,
        # TODO: user_answers не передаем, т.к. сервис их не обрабатывает на этом этапе
    )

    if not next_question_data_result.get(
        "success"
    ) or not next_question_data_result.get("question"):
        # Обработка ошибки или если вопросов больше нет (неожиданно)
        error_message = next_question_data_result.get(
            "message", "Не удалось загрузить следующий вопрос."
        )
        await bot.edit_message_text(
            text=error_message,
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=None,
        )
        # TODO: Возможно, стоит очистить состояние FSM или предложить завершить тест
        return

    new_question_details = next_question_data_result["question"]
    new_current_index = next_question_data_result["current_question_index"]

    # Обновляем FSM
    await state.update_data(
        current_question_index=new_current_index,
        current_question_details=new_question_details,
    )

    # Формируем сообщение и клавиатуру для нового вопроса
    message_text = f"<b>Тест по курсу: {course_title}</b>\n\n"
    message_text += f"Вопрос {new_question_details['order']}/{total_questions}:\n"
    message_text += clean_html_for_telegram(new_question_details["text"])

    keyboard = build_question_keyboard(
        question_id=new_question_details["id"],
        options=new_question_details["options"],
        is_multiple_choice=new_question_details["is_multiple_choice"],
        course_id=course_id,
        all_questions_ids_str=",".join(
            map(str, all_questions_ids)
        ),  # all_questions_ids не меняется
        current_question_index=new_current_index,
        total_questions=total_questions,
        selected_answers_ids=set(),  # Новый вопрос, выбранных ответов нет
    )

    try:
        await bot.edit_message_text(
            text=message_text,
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=keyboard.as_markup(),
        )
    except Exception as e:
        print(f"Error editing message for next question: {e}")


@testing_router.callback_query(
    F.data.startswith(CB_TEST_ACTION_FINISH) & TestState.in_progress
)
async def process_finish_test(
    callback: CallbackQuery, state: FSMContext, bot: Bot, test_service: TestService
):
    """
    Обрабатывает нажатие кнопки "Завершить тест".
    Подсчитывает результаты, сохраняет их и выводит пользователю.
    """
    await callback.answer()

    fsm_data = await state.get_data()
    course_id = fsm_data["course_id"]
    user_answers = fsm_data.get("user_answers", {})
    message_id_to_edit = fsm_data["message_id_to_edit"]
    chat_id = fsm_data["chat_id"]

    if not user_answers:
        # Если пользователь нажал "Завершить", не ответив ни на один вопрос
        await bot.edit_message_text(
            text="Вы не ответили ни на один вопрос. Тест не может быть засчитан.",
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=None,
        )
        await state.clear()
        return

    submission_result = await test_service.submit_test(
        telegram_id=callback.from_user.id,
        course_id=course_id,
        user_answers=user_answers,
    )

    await state.clear()  # Очищаем состояние FSM после получения результатов от сервиса

    if not submission_result.get("success"):
        error_message = submission_result.get(
            "message", "Не удалось завершить тест и получить результаты."
        )
        await bot.edit_message_text(
            text=error_message,
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=None,
        )
        return

    # Формируем сообщение с результатами
    score = submission_result.get("score_percentage", 0)
    correct_answers = submission_result.get("correct_answers_count", 0)
    total_questions = submission_result.get("total_questions_count", 0)
    passed = submission_result.get("passed", False)
    course_title = submission_result.get("course_title", "")

    result_message_text = f"<b>Тест по курсу «{course_title}» завершен!</b>\n\n"
    result_message_text += f"Ваш результат: <b>{score}%</b>\n"
    result_message_text += f"Правильных ответов: {correct_answers}/{total_questions}\n"

    if passed:
        result_message_text += "\n🎉 Поздравляем, тест <b>УСПЕШНО</b> сдан!"
    else:
        result_message_text += "\nК сожалению, тест <b>НЕ СДАН</b>. Попробуйте еще раз!"

    image_to_send_path = submission_result.get("image_path")

    results_keyboard_builder = InlineKeyboardBuilder()
    results_keyboard_builder.row(
        InlineKeyboardButton(
            text="К темам курса 📖", callback_data=f"course:{course_id}"
        )
    )

    try:
        if image_to_send_path:
            try:
                image = FSInputFile(image_to_send_path)
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=image,
                    caption=result_message_text,
                    reply_markup=results_keyboard_builder.as_markup(),
                )
                await bot.delete_message(chat_id=chat_id, message_id=message_id_to_edit)
            except Exception as e_img:
                print(f"Error sending test result image: {e_img}")
                await bot.edit_message_text(
                    text=result_message_text,
                    chat_id=chat_id,
                    message_id=message_id_to_edit,
                    reply_markup=results_keyboard_builder.as_markup(),
                )
        else:
            await bot.edit_message_text(
                text=result_message_text,
                chat_id=chat_id,
                message_id=message_id_to_edit,
                reply_markup=results_keyboard_builder.as_markup(),
            )
    except Exception as e:
        print(f"Error displaying test results: {e}")
        await bot.send_message(
            chat_id=chat_id,
            text=result_message_text,
            reply_markup=results_keyboard_builder.as_markup(),
        )


@testing_router.callback_query(F.data.startswith("test_action:show_results:"))
async def process_show_test_results(
    callback: CallbackQuery, bot: Bot, test_service: TestService
) -> None:
    """
    Обрабатывает нажатие кнопки "Показать результаты" для ранее завершенного теста.
    """
    await callback.answer()
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.message.answer("Неверные данные для показа результатов теста.")
        return
    try:
        course_id = int(parts[2])
    except ValueError:
        await callback.message.answer("Некорректный идентификатор курса.")
        return
    # Получаем статистику из репозитория тестов
    stats = await test_service.user_test_repo.count_results(
        user_id=callback.from_user.id, course_id=course_id
    )
    if not stats:
        await callback.message.answer("Результаты тестирования не найдены.")
        return

    # Определяем company_id пользователя
    user = await test_service.user_repo.get_by_telegram_id(callback.from_user.id)
    company_id = getattr(user, "company_id", None)
    image_path = await test_service.settings_repo.get_test_result_image_path(
        passed=stats.get("is_complete", False), company_id=company_id
    )
    # Формируем текст с результатами
    result_message = (
        f"<b>Результаты теста по курсу «{stats.get('course_title','')}»</b>\n\n"
        f"Ваш результат: <b>{stats.get('correct_percent',0)}%</b>\n"
        f"Правильных ответов: {stats.get('correct_count',0)}/{stats.get('total_count',0)}\n"
    )
    if stats.get("is_complete"):
        result_message += "\n🎉 Тест <b>УСПЕШНО</b> сдан!"
    else:
        result_message += "\nК сожалению, тест <b>НЕ СДАН</b>."
    # Кнопка возврата к списку тем курса
    from app.bot.telegram.keyboards.builders import InlineKeyboardBuilder

    back_button = InlineKeyboardButton(
        text="🔙 К темам курса", callback_data=f"course:{course_id}"
    )
    keyboard = InlineKeyboardBuilder.create_inline_kb([[back_button]])
    # Отправка фото или текста
    try:
        if image_path and os.path.exists(image_path):
            photo = FSInputFile(image_path)
            await callback.message.answer_photo(
                photo=photo, caption=result_message, reply_markup=keyboard
            )
        else:
            await callback.message.answer(result_message, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(result_message, reply_markup=keyboard)
