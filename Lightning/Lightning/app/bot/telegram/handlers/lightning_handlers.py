from datetime import timedelta
from typing import Dict, Set, List

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from django.utils import timezone

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
from app.bot.telegram.keyboards.lightning_kb import (
    get_lightning_main_menu_kb,
    get_period_filter_kb,
    get_lightnings_list_kb,
    get_lightning_actions_kb,
    get_question_kb,
    get_retry_kb,
)
from app.bot.telegram.selectors.lightning_selectors import (
    get_user_by_telegram_id,
    list_relevant_lightnings,
    list_unread_lightnings,
    list_questions,
    list_answers,
    get_read_record,
    get_test_record,
    get_attempt_record,
    get_lightnings_status,
)
from app.bot.telegram.services.lightning_services import (
    mark_lightning_as_read,
    delete_previous_test_result,
    finalize_test_sync,
    ck_to_tg_html,
)
from app.lightning.models import LightningQuestion, LightningRead

router = Router(name="lightning_router")


# -----------------------------
# FSM: храним выборы ответов
# -----------------------------
# TODO перенести в State
class TestStates(StatesGroup):
    testing = State()  # активная сессия теста


# -----------------------------
# Вспомогательные функции
# -----------------------------
def _period_to_since(period: str):
    now = timezone.now()
    if period == "week":
        return now - timedelta(days=7)
    if period == "month":
        return now - timedelta(days=31)
    if period == "three_months":
        return now - timedelta(days=90)
    if period == "six_months":
        return now - timedelta(days=180)
    return None  # "всё время"


async def _get_read_ids(user_id: int, lightning_ids: List[int]) -> Set[int]:
    ids = (
        await LightningRead.objects.filter(
            user_id=user_id, lightning_id__in=lightning_ids, is_read=True
        )
        .values_list("lightning_id", flat=True)
        .aall()
    )
    return set(ids)


def _format_question_text(
    idx: int, total: int, q: LightningQuestion, answers: List
) -> str:
    # Текст вопроса: заголовок + перечень вариантов (номер + текст).
    parts = [
        "<b>Тестирование</b>\n",
        f"Вопрос ({idx + 1} из {total}):\n",
        f"<i>{q.name}</i>\n\n",
    ]
    for pos, ans in enumerate(answers, start=1):
        parts.append(f"<b>{pos})</b> {ans.text}\n\n")
    parts.append(
        "Выберите несколько ответов\n"
        if q.is_multiple_choice
        else "Выберите один ответ\n"
    )
    return "".join(parts)


# -----------------------------
# Точки входа (меню)
# -----------------------------
@router.message((F.text == "🌩️ Молнии / Chaqmoqlar") | (F.text == "Молнии"))
async def lightning_menu(message: Message):
    # показываем фильтры периодов
    await message.answer(
        "Выберите период:\nDavrni tanlang:", reply_markup=get_period_filter_kb()
    )


@router.message(
    (F.text == "🌩️ Не прочитанные молнии / O‘qilmagan chaqmoqlar") |
    (F.text == "Не прочитанные молнии")
)
async def lightning_unread(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Пользователь не найден.")
        return

    lightnings = await list_unread_lightnings(user.id, since=None)
    ids = [l.id for l in lightnings]
    status = await get_lightnings_status(user.id, ids) if ids else {}

    if lightnings:
        kb = get_lightnings_list_kb(lightnings, status=status)
        await message.answer(
            "Непрочитанные молнии:\nO‘qilmagan chaqmoqlar:", reply_markup=kb
        )
    else:
        await message.answer("Нет доступных молний / Mavjud chaqmoqlar yo‘q")


# -----------------------------
# Фильтр по периоду
# -----------------------------
@router.callback_query(PeriodFilterCB.filter())
async def filter_period(callback: CallbackQuery, callback_data: PeriodFilterCB):
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.answer("Пользователь не найден.")
        await callback.answer()
        return

    since = _period_to_since(callback_data.period)
    lightnings = await list_relevant_lightnings(user.id, since=since)
    ids = [l.id for l in lightnings]
    status = await get_lightnings_status(user.id, ids) if ids else {}

    if lightnings:
        kb = get_lightnings_list_kb(lightnings, status=status)
        await callback.message.edit_text(
            "Доступные молнии:\nMavjud chaqmoqlar:", reply_markup=kb
        )
    else:
        await callback.message.edit_text(
            "Нет доступных молний / Mavjud chaqmoqlar yo‘q"
        )
    await callback.answer()


# -----------------------------
# Открыть молнию
# -----------------------------
@router.callback_query(OpenLightningCB.filter())
async def open_lightning(callback: CallbackQuery, callback_data: OpenLightningCB):
    # из за видео падали ошибки от телеграм bad request (телеграм ожидает 60 секунд если нет answer, то отправляет ошибку в логи)
    await callback.answer("Загружаю материалы, пожалуйста, подождите/Materiallar yuklanmoqda, iltimos bir oz kutib turing")

    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.answer("Пользователь не найден.")
        return

    from app.bot.telegram.selectors.lightning_selectors import get_lightning

    lightning = await get_lightning(callback_data.lightning_id)
    if not lightning:
        await callback.message.answer("Молния недоступна.")
        return

    # 1) Медиа сверху
    try:
        if lightning.image:
            await callback.message.answer_photo(FSInputFile(lightning.image.path))
        if lightning.file:
            await callback.message.answer_document(FSInputFile(lightning.file.path))
    except Exception:
        pass

    # 2) Текст
    if lightning.content:
        text = ck_to_tg_html(lightning.content)
        if text and text.strip():
            await callback.message.answer(text, parse_mode="HTML")

    # 3) Кнопки действий
    questions = await list_questions(lightning.id)
    has_questions = bool(questions)

    show_actions = True
    if has_questions:
        test_record = await get_test_record(user.id, lightning.id)
        if test_record and test_record.complete:
            show_actions = False
    else:
        read_record = await get_read_record(user.id, lightning.id)
        if read_record and getattr(read_record, "is_read", False):
            show_actions = False

    if show_actions:
        kb = get_lightning_actions_kb(lightning.id, has_questions=has_questions)
        await callback.message.answer(
            "Для продолжения выберите:\nDavom etish uchun tanlang:", reply_markup=kb
        )


# -----------------------------
# Ознакомился (без теста)
# -----------------------------
@router.callback_query(MarkReadCB.filter())
async def mark_read(callback: CallbackQuery, callback_data: MarkReadCB):
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.answer("Пользователь не найден.")
        await callback.answer()
        return

    await mark_lightning_as_read(user.id, callback_data.lightning_id, value=True)

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer()


# -----------------------------
# Старт теста
# -----------------------------
@router.callback_query(StartTestCB.filter())
async def start_test(
    callback: CallbackQuery, callback_data: StartTestCB, state: FSMContext
):
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.answer("Пользователь не найден.")
        await callback.answer()
        return

    l_id = callback_data.lightning_id

    # отмечаем прочитано и убираем прошлый результат
    await mark_lightning_as_read(user.id, l_id, value=True)
    await delete_previous_test_result(user.id, l_id)

    # инициализируем FSM
    await state.set_state(TestStates.testing)
    await state.update_data(
        lightning_id=l_id,
        idx=0,
        selected_map={},  # {str(q_id): [answer_ids]}
    )

    # показываем первый вопрос
    questions = await list_questions(l_id)
    if not questions:
        await callback.message.answer("Для этой молнии нет вопросов.")
        await callback.answer()
        return

    q = questions[0]
    answers = await list_answers(q.id)
    text = _format_question_text(0, len(questions), q, answers)

    kb = get_question_kb(
        lightning_id=l_id,
        question_id=q.id,
        answers=answers,
        selected_answer_ids=set(),  # пока ничего не выбрано
        is_multiple_choice=q.is_multiple_choice,
        current_question_index=0,
        total_questions=len(questions),
        can_finish_test=False,  # первый вопрос — не завершаем
    )
    await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# -----------------------------
# Выбор/переключение ответа
# -----------------------------
@router.callback_query(AnswerCB.filter(), TestStates.testing)
async def answer_toggle(
    callback: CallbackQuery, callback_data: AnswerCB, state: FSMContext
):
    data = await state.get_data()
    l_id: int = data["lightning_id"]
    idx: int = data["idx"]
    selected_map: Dict[str, List[int]] = data.get("selected_map", {})

    # текущий вопрос по индексу
    questions = await list_questions(l_id)
    if not questions or idx >= len(questions):
        await callback.answer()
        return

    q = questions[idx]
    q_key = str(q.id)
    current = set(selected_map.get(q_key, []))

    # toggle / replace в зависимости от multiple
    if q.is_multiple_choice:
        if callback_data.answer_id in current:
            current.remove(callback_data.answer_id)
        else:
            current.add(callback_data.answer_id)
        selected_map[q_key] = sorted(current)
    else:
        selected_map[q_key] = [callback_data.answer_id]

    # перерисовываем этот же вопрос
    answers = await list_answers(q.id)
    text = _format_question_text(idx, len(questions), q, answers)

    can_finish = (idx == len(questions) - 1) and bool(selected_map.get(q_key, []))
    kb = get_question_kb(
        lightning_id=l_id,
        question_id=q.id,
        answers=answers,
        selected_answer_ids=set(selected_map.get(q_key, [])),
        is_multiple_choice=q.is_multiple_choice,
        current_question_index=idx,
        total_questions=len(questions),
        can_finish_test=can_finish,
    )

    await state.update_data(selected_map=selected_map)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# -----------------------------
# Навигация по вопросам
# -----------------------------
@router.callback_query(NavCB.filter(), TestStates.testing)
async def question_nav(
    callback: CallbackQuery, callback_data: NavCB, state: FSMContext
):
    data = await state.get_data()
    l_id: int = data["lightning_id"]
    selected_map: Dict[str, List[int]] = data.get("selected_map", {})

    questions = await list_questions(l_id)
    if not questions:
        await callback.answer()
        return

    new_idx = callback_data.current_question_index
    if new_idx < 0 or new_idx >= len(questions):
        await callback.answer()
        return

    q = questions[new_idx]
    answers = await list_answers(q.id)

    sel = set(selected_map.get(str(q.id), []))
    text = _format_question_text(new_idx, len(questions), q, answers)

    can_finish = (new_idx == len(questions) - 1) and bool(sel)
    kb = get_question_kb(
        lightning_id=l_id,
        question_id=q.id,
        answers=answers,
        selected_answer_ids=sel,
        is_multiple_choice=q.is_multiple_choice,
        current_question_index=new_idx,
        total_questions=len(questions),
        can_finish_test=can_finish,
    )

    await state.update_data(idx=new_idx)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# -----------------------------
# Завершить тест
# -----------------------------
@router.callback_query(FinishTestCB.filter(), TestStates.testing)
async def finish_test(
    callback: CallbackQuery, callback_data: FinishTestCB, state: FSMContext
):
    data = await state.get_data()
    l_id: int = data["lightning_id"]
    selected_map_raw: Dict[str, List[int]] = data.get("selected_map", {})

    # преобразуем к {int: set[int]}
    selected_map = {int(k): set(v) for k, v in selected_map_raw.items()}

    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.answer("Пользователь не найден.")
        await callback.answer()
        return

    score = await finalize_test_sync(user.id, l_id, selected_map)

    # показываем результат
    msg = (
        f"Ваш результат по тесту:\n"
        f"Test natijalaringiz:\n\n"
        f"<b>Верных ответов / To‘g‘ri javoblar:</b> {score.correct_percent}%\n"
        f"<b>Неверных ответов / Noto‘g‘ri javoblar:</b> {score.incorrect_percent}%\n\n"
    )
    if score.complete:
        msg += "Поздравляем, вы успешно сдали тест! ✅\nTabriklaymiz, siz testni muvaffaqiyatli topshirdingiz! ✅"
        await callback.message.answer(msg, parse_mode="HTML")
    else:
        msg += "К сожалению, вы не сдали тест. ❌\nAfsuski, siz testdan o‘ta olmadingiz. ❌"
        await callback.message.answer(msg, parse_mode="HTML")

        # узнали текущее число попыток
        attempt = await get_attempt_record(user.id, l_id)
        if attempt and attempt.attempts >= 3:
            await callback.message.answer(
                "Вы 3 раза не сдали тест. Рекомендуем обратиться к руководителю для очного инструктажа.\n"
                "Siz testni 3 marta topshira olmadingiz. Yuzma-yuz yo‘riqnoma olish uchun rahbarga murojaat qilishingiz tavsiya etiladi."
            )
        else:
            await callback.message.answer(
                "Попробуйте пройти тест снова:\nTestni yana bir bor topshirib ko‘ring:",
                reply_markup=get_retry_kb(l_id),
            )

    # выходим из состояния теста
    await state.clear()
    await callback.answer()


# -----------------------------
# Повтор теста
# -----------------------------
@router.callback_query(RetryTestCB.filter())
async def retry_test(
    callback: CallbackQuery, callback_data: RetryTestCB, state: FSMContext
):
    # фактически то же, что и старт теста
    await start_test(
        callback, StartTestCB(lightning_id=callback_data.lightning_id), state
    )
