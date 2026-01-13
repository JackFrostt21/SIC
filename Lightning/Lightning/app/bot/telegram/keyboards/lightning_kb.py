from typing import Iterable, Sequence, Set
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


from app.bot.telegram.callbacks.lightning_cb import (
    PeriodFilterCB,
    OpenLightningCB,
    MarkReadCB,
    StartTestCB,
    AnswerCB,
    NavCB,
    FinishTestCB,
    RetryTestCB,
)

# ---------- Главная клавиатура  ----------


def get_lightning_main_menu_kb() -> ReplyKeyboardMarkup:
    """
    Основная reply клавиатура, для начала работы с ботом
    Молнии: список доступных молний (не черновики + таргетинг)
    Не прочитанные молнии: список не прочитанных молний или не сданных тестов
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="🌩️ Молнии / Chaqmoqlar")],
            [KeyboardButton(text="🌩️ Не прочитанные молнии / O‘qilmagan chaqmoqlar")],
        ],
    )


# ---------- Клавиатура фильтра периодов списка ----------


def get_period_filter_kb() -> InlineKeyboardMarkup:
    """
    Кнопки фильтра периода: Неделя / Месяц / 3 месяца / 6 месяцев
    Выводит доступные молнии (не черновики + таргетинг) по выбранному периоду
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Неделя / Hafta", callback_data=PeriodFilterCB(period="week").pack()
    )
    keyboard.button(
        text="Месяц / Oy", callback_data=PeriodFilterCB(period="month").pack()
    )
    keyboard.button(
        text="3 месяца / 3 oy",
        callback_data=PeriodFilterCB(period="three_months").pack(),
    )
    keyboard.button(
        text="6 месяцев / 6 oy",
        callback_data=PeriodFilterCB(period="six_months").pack(),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


# ---------- Клавиатура списка молний ----------


def get_lightnings_list_kb(
    lightnings: list,
    status: dict[int, dict] | None = None,
) -> InlineKeyboardMarkup:
    """
    Список молний с кнопками открытия и статусами прохождения.

    Args:
        lightnings: Список объектов молний
        status: Словарь статусов прохождения в формате:
            {
                lightning_id: {
                    "has_questions": bool,    # Есть ли вопросы в молнии
                    "is_completed": bool      # Прошел ли пользователь молнию
                }
            }
            Если None - статусы не отображаются

    Returns:
        InlineKeyboardMarkup: Клавиатура со списком молний
    """
    keyboard = InlineKeyboardBuilder()

    for lightning in lightnings:
        status_icon = ""
        if status is not None:
            lightning_status = status.get(lightning.id)
            if lightning_status:
                if lightning_status["is_completed"]:
                    status_icon = "✅ "
                else:
                    status_icon = "❓ " if lightning_status["has_questions"] else "📄 "
        button_text = f"{status_icon}{lightning.name}"
        keyboard.button(
            text=button_text,
            callback_data=OpenLightningCB(lightning_id=lightning.id).pack(),
        )

    keyboard.adjust(1)
    return keyboard.as_markup()


# ---------- Клавиатура действий молнии ----------


def get_lightning_actions_kb(
    lightning_id: int,
    has_questions: bool,
) -> InlineKeyboardMarkup:
    """
    Генерируем кнопку после основного текста молнии.
    Если есть вопросы — “Пройти тест”.
    Если вопросов нет — “Ознакомился”.
    """
    keyboard = InlineKeyboardBuilder()
    if has_questions:
        keyboard.button(
            text="Пройти тест / Testni topshirish",
            callback_data=StartTestCB(lightning_id=lightning_id).pack(),
        )
    else:
        keyboard.button(
            text="✅ Ознакомился / Bilmoqdaman",
            callback_data=MarkReadCB(lightning_id=lightning_id).pack(),
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


# ---------- Клавиатура теста: варианты ответов + навигация ----------

UNSELECTED = "⚪"
SELECTED = "🟢"


def get_question_kb(
    lightning_id: int,
    question_id: int,
    answers: Sequence,  # Список вариантов ответов (LightningAnswer)
    selected_answer_ids: set[int] | None,  # какие ответы выбраны по текущему вопросу
    is_multiple_choice: bool,
    current_question_index: int,  # индекс текущего вопроса (0-based)
    total_questions: int,  # всего вопросов
    can_finish_test: bool,  # показывать “Завершить тест”
) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру для вопроса теста:
      - варианты ответов с маркерами выбора
      - навигацию между вопросами
      - кнопку завершения теста (при возможности)
    """
    selected_answer_ids = selected_answer_ids or set()
    keyboard = InlineKeyboardBuilder()

    # Кнопки вариантов ответов
    for position_number, answer in enumerate(answers, start=1):
        marker = SELECTED if answer.id in selected_answer_ids else UNSELECTED
        keyboard.row(
            InlineKeyboardButton(
                text=f"{marker} {position_number}",
                callback_data=AnswerCB(
                    lightning_id=lightning_id,
                    question_id=question_id,
                    answer_id=answer.id,
                ).pack(),
            )
        )

    # --- Навигация: одной строкой (если есть)
    nav_row: list[InlineKeyboardButton] = []
    if current_question_index > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="← Предыдущий / Orqaga",
                callback_data=NavCB(
                    lightning_id=lightning_id,
                    current_question_index=current_question_index - 1,
                    move="prev",
                ).pack(),
            )
        )
    if current_question_index < total_questions - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="Следующий → / Keyingi",
                callback_data=NavCB(
                    lightning_id=lightning_id,
                    current_question_index=current_question_index + 1,
                    move="next",
                ).pack(),
            )
        )
    if nav_row:
        keyboard.row(*nav_row)

    # --- Кнопка завершения: отдельной строкой
    if can_finish_test:
        keyboard.row(
            InlineKeyboardButton(
                text="🏁 Завершить тест / Testni tugatish",
                callback_data=FinishTestCB(lightning_id=lightning_id).pack(),
            )
        )

    print()

    return keyboard.as_markup()


# ---------- Клавиатура повтора теста ----------


def get_retry_kb(lightning_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔁 Пройти тест повторно / Testni qayta topshirish",
        callback_data=RetryTestCB(lightning_id=lightning_id).pack(),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
