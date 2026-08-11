from typing import List, Dict, Any, Optional, Set

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Префиксы для callback_data в клавиатурах тестирования
CB_TEST_ANSWER_SELECT = "test_ans:select"
CB_TEST_QUESTION_NEXT = "test_qst:next"
CB_TEST_QUESTION_PREV = "test_qst:prev"
CB_TEST_ACTION_FINISH = "test_act:finish"


def build_question_keyboard(
    question_id: int,
    options: List[Dict[str, Any]],
    is_multiple_choice: bool,
    course_id: int,
    all_questions_ids_str: str,
    current_question_index: int,
    total_questions: int,
    selected_answers_ids: Optional[Set[int]] = None,
) -> InlineKeyboardBuilder:
    """
    Собирает клавиатуру для вопроса теста.

    Args:
        question_id: ID текущего вопроса.
        options: Список словарей с вариантами ответов ({'id': int, 'text': str, 'order': int}).
        is_multiple_choice: True, если вопрос допускает несколько ответов.
        course_id: ID курса.
        all_questions_ids_str: Строка с ID всех вопросов теста, разделенных запятой.
        current_question_index: Индекс текущего вопроса (0-based).
        total_questions: Общее количество вопросов в тесте.
        selected_answers_ids: Множество ID уже выбранных ответов для этого вопроса.

    Returns:
        InlineKeyboardBuilder: Готовая клавиатура.
    """
    builder = InlineKeyboardBuilder()
    if selected_answers_ids is None:
        selected_answers_ids = set()

    for option in sorted(options, key=lambda opt: opt.get("order", 0)):
        option_id = option["id"]
        option_order = option["order"]  # Используем порядковый номер вместо текста
        prefix = "☑️ " if option_id in selected_answers_ids else "◻️ "
        if not is_multiple_choice and option_id in selected_answers_ids:
            prefix = "🔘 "  # Радио-кнопка для одиночного выбора
        elif not is_multiple_choice:
            prefix = "⚪️ "

        # Callback_data для выбора ответа:
        # test_ans:select:<course_id>:<q_idx>:<all_q_ids_str>:<q_id>:<opt_id>:<is_multi_0_or_1>
        # Пока что сделаем callback, который всегда будет обрабатываться на сервере для простоты.
        is_multi_flag = 1 if is_multiple_choice else 0
        # Было: test_ans:select:<course_id>:<q_idx>:<all_q_ids_str>:<q_id>:<opt_id>:<is_multi>
        callback_data = (
            f"{CB_TEST_ANSWER_SELECT}:{question_id}:{option_id}:{is_multi_flag}"
        )
        try:
            cb_len = len(callback_data)
            if cb_len > 60:
                print(
                    f"[TEST KB] WARNING callback len={cb_len} q_id={question_id} opt_id={option_id}"
                )
        except Exception as e:
            print(f"[TEST KB] ERROR len(callback_data): {e}")
        builder.row(
            InlineKeyboardButton(
                text=f"{prefix}{option_order}", callback_data=callback_data
            )
        )

    # Кнопки навигации и завершения
    nav_buttons = []
    # Кнопка "Назад"
    if current_question_index > 0:
        # Было: f"{CB_TEST_QUESTION_PREV}:{course_id}:{current_question_index}:{all_questions_ids_str}"
        prev_cb_data = f"{CB_TEST_QUESTION_PREV}"
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=prev_cb_data)
        )
    # Кнопка "Далее" или "Завершить"
    if current_question_index < total_questions - 1:
        # Было: f"{CB_TEST_QUESTION_NEXT}:{course_id}:{current_question_index}:{all_questions_ids_str}"
        next_cb_data = f"{CB_TEST_QUESTION_NEXT}"
        try:
            next_len = len(next_cb_data)
            if next_len > 60:
                print(
                    f"[TEST KB] WARNING next len={next_len} q_idx={current_question_index}"
                )
        except Exception as e:
            print(f"[TEST KB] ERROR len(next_cb_data): {e}")
        nav_buttons.append(
            InlineKeyboardButton(text="Далее ➡️", callback_data=next_cb_data)
        )
    else:
        # Было: f"{CB_TEST_ACTION_FINISH}:{course_id}"
        finish_cb_data = f"{CB_TEST_ACTION_FINISH}"
        try:
            finish_len = len(finish_cb_data)
            if finish_len > 60:
                print(f"[TEST KB] WARNING finish len={finish_len}")
        except Exception as e:
            print(f"[TEST KB] ERROR len(finish_cb_data): {e}")
        nav_buttons.append(
            InlineKeyboardButton(text="Завершить тест 🏁", callback_data=finish_cb_data)
        )
    builder.row(*nav_buttons)
    return builder
