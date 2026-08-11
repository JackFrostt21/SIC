from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
import logging

from app.learning_app.services.test_service import TestService

from app.bot.telegram.keyboards.test_kb import (
    build_question_keyboard,
    CB_TEST_ACTION_FINISH,
    CB_TEST_ANSWER_SELECT,
    CB_TEST_QUESTION_NEXT,
    CB_TEST_QUESTION_PREV,
)
from app.bot.telegram.states.test_state import TestState
from app.bot.telegram.utils.text_formatters import clean_html_for_telegram


router = Router(name="testing_router")
logger = logging.getLogger(__name__)


def format_question_with_options(question_data, total_questions):
    """
    Формирует текст вопроса с вариантами ответов

    Args:
        question_data: Данные вопроса с options
        total_questions: Общее количество вопросов

    Returns:
        str: Отформатированный текст вопроса с вариантами ответов
    """
    message_text = f"Вопрос {question_data['order']}/{total_questions}:\n"
    message_text += clean_html_for_telegram(question_data["text"]) + "\n"
    if question_data.get("is_multiple_choice"):
        message_text += "(Выберете несколько правильных ответов)\n\n"
    else:
        message_text += "(Выберете один правильный ответ)\n\n"

    # Добавляем варианты ответов с порядковыми номерами
    sorted_options = sorted(
        question_data["options"], key=lambda opt: opt.get("order", 0)
    )
    for option in sorted_options:
        message_text += (
            f"{option['order']}. {clean_html_for_telegram(option['text'])}\n"
        )

    return message_text


@router.callback_query(F.data.startswith("test_action:start"))
async def process_start_test(
    callback: CallbackQuery, state: FSMContext, bot: Bot, test_service: TestService
):
    """
    Обработчик нажатия кнопки "Начать тест" или "Повторить тест".
    Запускает новый тест или перезапускает существующий (если пользователь был в процессе).
    """
    await callback.answer()
    logger.info(f"[TEST START] callback_data={callback.data} user={callback.from_user.id}")
    parts = callback.data.split(":")
    topic_id = None
    course_id = None
    # Форматы:
    # - test_action:start:<course_id>
    # - test_action:start_topic:<course_id>:<topic_id>
    try:
        if len(parts) >= 4 and parts[1] == "start_topic":
            course_id = int(parts[2])
            topic_id = int(parts[3])
        elif len(parts) >= 3 and parts[1] == "start":
            course_id = int(parts[2])
        else:
            raise ValueError(f"Unexpected callback format: {callback.data}")
    except Exception as e:
        logger.error(f"[TEST START] parse error for data={callback.data}: {e}")
        await callback.message.answer("Некорректные данные для теста.")
        return
    logger.info(f"[TEST START] parsed course_id={course_id} topic_id={topic_id}")

    current_state = await state.get_state()
    if current_state == TestState.in_progress:
        await state.clear()  # Очищаем предыдущее состояние, если было

    initial_test_data = await test_service.start_test_attempt(
        telegram_id=callback.from_user.id, course_id=course_id, topic_id=topic_id
    )
    logger.info(f"[TEST START] service response success={initial_test_data.get('success')} msg={initial_test_data.get('message')}")

    if not initial_test_data.get("success"):
        msg = initial_test_data.get("message", "Не удалось начать тест.")
        sent = False
        # Сообщение могло быть фото/без текста — пробуем редактировать, иначе отправляем новое
        try:
            await callback.message.edit_text(msg)
            sent = True
        except Exception:
            try:
                await callback.message.edit_caption(msg)
                sent = True
            except Exception:
                pass
        # Если редактировать не получилось — шлём новое сообщение
        if not sent:
            try:
                await callback.message.answer(msg)
                sent = True
            except Exception:
                logger.warning("[TEST START] Failed to send failure message via answer()")
        # В любом случае отправим явное сообщение в чат (чтобы пользователь увидел)
        try:
            chat_id = callback.message.chat.id
            await bot.send_message(chat_id=chat_id, text=msg)
        except Exception:
            logger.warning("[TEST START] Failed to send failure message via send_message")
        # Просто отвечаем на callback, чтобы убрать "часики", без алерта
        try:
            await callback.answer()
        except Exception:
            pass
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

    title = initial_test_data.get("topic_title") or initial_test_data.get(
        "course_title"
    )
    message_text = f"<b>Тест: {title}</b>\n\n"
    message_text += format_question_with_options(question_data, total_questions)
    try:
        print(
            f"[TEST START] q_id={question_data['id']} options={len(question_data['options'])} total={total_questions} msg_len={len(message_text)}"
        )
    except Exception as e:
        print(f"[TEST START] ERROR logging start info: {e}")

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
        topic_id=topic_id,
        topic_title=initial_test_data.get("topic_title"),
        all_questions_ids=all_q_ids,
        current_question_index=current_q_idx,
        user_answers={},
        total_questions=total_questions,
        message_id_to_edit=sent_message.message_id,
        chat_id=callback.message.chat.id,  # chat_id для редактирования сообщения
        current_question_details=question_data,
    )


@router.callback_query(
    F.data.startswith(CB_TEST_ANSWER_SELECT), StateFilter(TestState.in_progress)
)
async def process_select_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обрабатывает выбор/снятие выбора ответа на вопрос.
    Обновляет клавиатуру сообщения с вопросом.
    """
    await callback.answer()  # Сразу отвечаем на callback, чтобы кнопка не "зависала"

    try:
        print(f"[TEST SELECT] cb_len={len(callback.data)} data={callback.data}")
    except Exception:
        pass

    parts = callback.data.split(":")

    # Поддержка двух форматов:
    # Новый короткий: ["test_ans","select", <q_id>, <opt_id>, <is_multi>]
    # Старый длинный: ["test_ans","select", <course_id>, <q_idx>, <all_q_ids_str>, <q_id>, <opt_id>, <is_multi>]
    try:
        if len(parts) == 5:
            # Новый короткий формат
            question_id_from_cb = int(parts[2])
            selected_option_id = int(parts[3])
            is_multiple_choice_from_cb = bool(int(parts[4]))
        else:
            # Старый формат (обратная совместимость)
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

    try:
        print(
            f"[TEST SELECT] q_id={question_id_from_cb} opt_id={selected_option_id} multi={is_multiple_choice_from_cb} curr_q={current_question_details.get('id') if current_question_details else 'None'}"
        )
    except Exception:
        pass
    try:
        print(
            f"[TEST SELECT] answers_for_q={list(current_answers_for_question)} total_answers_keys={len(user_answers)}"
        )
    except Exception:
        pass

    # Обновляем клавиатуру
    keyboard = build_question_keyboard(
        question_id=current_question_details["id"],
        options=current_question_details["options"],
        is_multiple_choice=current_question_details["is_multiple_choice"],
        course_id=fsm_data["course_id"],
        all_questions_ids_str=",".join(map(str, fsm_data["all_questions_ids"])),
        current_question_index=fsm_data["current_question_index"],
        total_questions=fsm_data["total_questions"],
        selected_answers_ids=current_answers_for_question,
    )

    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=keyboard.as_markup(),
        )
    except Exception as e:
        print(f"Error editing message reply markup: {e}")


@router.callback_query(
    F.data.startswith(CB_TEST_QUESTION_NEXT), StateFilter(TestState.in_progress)
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
    topic_id = fsm_data.get("topic_id")
    topic_title = fsm_data.get("topic_title")
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

    try:
        print(
            f"[TEST NEXT] course_id={course_id} idx={current_question_index}/{total_questions-1} all_ids={len(all_questions_ids)}"
        )
    except Exception:
        pass
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
    title_for_msg = topic_title or course_title
    message_text = f"<b>Тест: {title_for_msg}</b>\n\n"
    message_text += format_question_with_options(new_question_details, total_questions)
    try:
        print(
            f"[TEST NEXT] new_q_id={new_question_details['id']} options={len(new_question_details['options'])} msg_len={len(message_text)}"
        )
    except Exception:
        pass

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


@router.callback_query(
    F.data.startswith(CB_TEST_QUESTION_PREV), StateFilter(TestState.in_progress)
)
async def process_prev_question(
    callback: CallbackQuery, state: FSMContext, bot: Bot, test_service: TestService
):
    """
    Обрабатывает нажатие кнопки "Назад" для перехода к предыдущему вопросу.
    """
    await callback.answer()

    fsm_data = await state.get_data()
    course_id = fsm_data["course_id"]
    topic_id = fsm_data.get("topic_id")
    topic_title = fsm_data.get("topic_title")
    course_title = fsm_data["course_title"]
    all_questions_ids = fsm_data["all_questions_ids"]
    current_question_index = fsm_data["current_question_index"]
    total_questions = fsm_data["total_questions"]
    message_id_to_edit = fsm_data["message_id_to_edit"]
    chat_id = fsm_data["chat_id"]

    # Проверка, что это не первый вопрос
    if current_question_index <= 0:
        await bot.edit_message_text(
            text="Это был первый вопрос.",
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=None,
        )
        return

    try:
        print(
            f"[TEST PREV] course_id={course_id} idx={current_question_index}/{total_questions-1} all_ids={len(all_questions_ids)}"
        )
    except Exception:
        pass
    prev_question_data_result = await test_service.get_prev_question_data(
        course_id=course_id,
        all_questions_ids=all_questions_ids,
        current_question_index=current_question_index,
    )

    if not prev_question_data_result.get(
        "success"
    ) or not prev_question_data_result.get("question"):
        error_message = prev_question_data_result.get(
            "message", "Не удалось загрузить предыдущий вопрос."
        )
        await bot.edit_message_text(
            text=error_message,
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=None,
        )
        return

    new_question_details = prev_question_data_result["question"]
    new_current_index = prev_question_data_result["current_question_index"]

    # Обновляем FSM
    await state.update_data(
        current_question_index=new_current_index,
        current_question_details=new_question_details,
    )

    # Формируем сообщение и клавиатуру для предыдущего вопроса
    title_for_msg = topic_title or course_title
    message_text = f"<b>Тест: {title_for_msg}</b>\n\n"
    message_text += format_question_with_options(new_question_details, total_questions)
    try:
        print(
            f"[TEST PREV] new_q_id={new_question_details['id']} options={len(new_question_details['options'])} msg_len={len(message_text)}"
        )
    except Exception:
        pass

    keyboard = build_question_keyboard(
        question_id=new_question_details["id"],
        options=new_question_details["options"],
        is_multiple_choice=new_question_details["is_multiple_choice"],
        course_id=course_id,
        all_questions_ids_str=",".join(map(str, all_questions_ids)),
        current_question_index=new_current_index,
        total_questions=total_questions,
        selected_answers_ids=set(),
    )

    try:
        await bot.edit_message_text(
            text=message_text,
            chat_id=chat_id,
            message_id=message_id_to_edit,
            reply_markup=keyboard.as_markup(),
        )
    except Exception as e:
        print(f"Error editing message for prev question: {e}")


@router.callback_query(
    F.data.startswith(CB_TEST_ACTION_FINISH), StateFilter(TestState.in_progress)
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
    topic_id = fsm_data.get("topic_id")
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
        topic_id=topic_id,
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
    topic_title = submission_result.get("topic_title", "")
    title_for_msg = topic_title or course_title

    result_message_text = f"<b>Тест «{title_for_msg}» завершен!</b>\n\n"
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


# TODO: Удалить этот хендлер, т.к. он не используется
@router.callback_query(F.data.startswith("test_action:show_results:"))
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
    # Получаем пользователя
    user = await test_service.user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.answer("Пользователь не найден.")
        return

    # Получаем статистику из репозитория тестов
    stats = await test_service.user_test_repo.count_results(
        user_id=user.id, course_id=course_id
    )
    # Если тест еще не проходился (total_count = 0), показываем соответствующее сообщение
    if stats.get("total_count", 0) == 0:
        await callback.message.answer("Вы еще не проходили тест по этому курсу.")
        return
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
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 К темам курса", callback_data=f"course:{course_id}")
    keyboard = builder.as_markup()
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
