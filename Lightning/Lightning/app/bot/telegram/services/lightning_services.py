# app/bot/telegram/services/lightning_services.py
from __future__ import annotations

from typing import Dict, Iterable, Sequence, Set
from dataclasses import dataclass
from django.db import transaction
from asgiref.sync import sync_to_async

from app.lightning.models import (
    Lightning,
    LightningQuestion,
    LightningAnswer,
    LightningRead,
    LightningTest,
    UserTestAttempt,
)


# ---------------------------
# БАЗОВЫЕ ОПЕРАЦИИ / UPDATES
# ---------------------------

@sync_to_async
def mark_lightning_as_read(user_id: int, lightning_id: int, *, value: bool = True) -> LightningRead:
    """
    Помечает молнию как прочитанную/непрочитанную (по умолчанию True).
    Создаёт запись, если её не было.
    """
    obj, _ = LightningRead.objects.update_or_create(
        user_id=user_id,
        lightning_id=lightning_id,
        defaults={"is_read": value},
    )
    return obj


@sync_to_async
def delete_previous_test_result(user_id: int, lightning_id: int) -> int:
    """
    Удаляет запись LightningTest для пары (user, lightning).
    Возвращает количество удалённых записей (0 или 1).
    """
    deleted, _ = LightningTest.objects.filter(
        user_id=user_id, lightning_id=lightning_id
    ).delete()
    return deleted


@sync_to_async
def set_test_result(
    user_id: int,
    lightning_id: int,
    *,
    complete: bool,
    correct_percent: int,
    incorrect_percent: int,
) -> LightningTest:
    """
    Создаёт/обновляет запись результата теста.
    В модели quantity_* — это проценты (как в твоих verbose_name).
    """
    obj, _ = LightningTest.objects.update_or_create(
        user_id=user_id,
        lightning_id=lightning_id,
        defaults={
            "complete": complete,
            "quantity_correct": correct_percent,
            "quantity_not_correct": incorrect_percent,
        },
    )
    return obj


@sync_to_async
def inc_attempt_on_fail(user_id: int, lightning_id: int) -> int:
    """
    Увеличивает attempts на 1 при НЕуспешном тесте. Возвращает новое значение attempts.
    """
    obj, created = UserTestAttempt.objects.get_or_create(
        telegramuser_id=user_id,
        lightning_id=lightning_id,
        defaults={"attempts": 1},
    )
    if not created:
        obj.attempts += 1
        obj.save(update_fields=["attempts", "updated_at"])
    return obj.attempts


@sync_to_async
def reset_attempts(user_id: int, lightning_id: int) -> None:
    """
    Сбрасывает attempts в 0 (например, после успешного прохождения).
    """
    UserTestAttempt.objects.update_or_create(
        telegramuser_id=user_id,
        lightning_id=lightning_id,
        defaults={"attempts": 0},
    )


# ---------------------------
# ПОДСЧЁТ РЕЗУЛЬТАТА
# ---------------------------

@dataclass(frozen=True)
class TestScore:
    total_questions: int
    correct_count: int
    incorrect_count: int
    correct_percent: int
    incorrect_percent: int
    min_required: int
    complete: bool


def _calc_percent(numer: int, denom: int) -> int:
    if denom <= 0:
        return 0
    # как и раньше — целые проценты (floor)
    return (numer * 100) // denom


@sync_to_async
def _compute_score_sync(lightning_id: int, selected_map: dict[int, set[int]]) -> TestScore:
    """
    Считает результат по факту выбора ответов (в памяти), БД не меняет.
    selected_map: {question_id -> {answer_id, ...}}
    """
    # вопросы по молнии в порядке
    questions: list[LightningQuestion] = list(
        LightningQuestion.objects.filter(lightning_id=lightning_id).order_by("order", "id")
    )

    total = len(questions)
    correct = 0

    for q in questions:
        picked: set[int] = set(selected_map.get(q.id, set()))
        # правильные ответы по вопросу
        right_ids: set[int] = set(
            LightningAnswer.objects.filter(question_id=q.id, is_correct=True)
            .values_list("id", flat=True)
        )
        if picked and picked == right_ids:
            correct += 1

    incorrect = max(total - correct, 0)

    # мин. процент из молнии
    min_required = int(
        Lightning.objects.only("id", "min_test_percent_course").get(id=lightning_id).min_test_percent_course
    )

    correct_pct = _calc_percent(correct, total)
    incorrect_pct = 100 - correct_pct
    complete = correct_pct >= min_required

    return TestScore(
        total_questions=total,
        correct_count=correct,
        incorrect_count=incorrect,
        correct_percent=correct_pct,
        incorrect_percent=incorrect_pct,
        min_required=min_required,
        complete=complete,
    )


@sync_to_async
@transaction.atomic
def finalize_test_sync(
    user_id: int,
    lightning_id: int,
    selected_map: dict[int, set[int]],
) -> TestScore:
    """
    Финализирует тест:
      1) считает результат;
      2) пишет LightningTest (только проценты/факт);
      3) при провале — инкрементирует attempts; при успехе — сбрасывает attempts.
    Возвращает TestScore для показа пользователю.
    """
    score = _compute_score_sync.__wrapped__(lightning_id, selected_map)  # вызвать синхронную реализацию

    # сохраняем результат
    LightningTest.objects.update_or_create(
        user_id=user_id,
        lightning_id=lightning_id,
        defaults={
            "complete": score.complete,
            "quantity_correct": score.correct_percent,
            "quantity_not_correct": score.incorrect_percent,
        },
    )

    if score.complete:
        # успешная сдача — можно обнулить попытки (по желанию)
        UserTestAttempt.objects.update_or_create(
            telegramuser_id=user_id,
            lightning_id=lightning_id,
            defaults={"attempts": 0},
        )
    else:
        # провал — увеличиваем счётчик
        obj, created = UserTestAttempt.objects.get_or_create(
            telegramuser_id=user_id,
            lightning_id=lightning_id,
            defaults={"attempts": 1},
        )
        if not created:
            obj.attempts += 1
            obj.save(update_fields=["attempts", "updated_at"])

    return score


"""Чистка HTML для Telegram"""
import re
from html import unescape
import bleach

# Разрешённые Telegram-HTML теги и атрибуты (минимально безопасный набор)
ALLOWED_TAGS = ["b", "strong", "i", "em", "u", "s", "strike", "del", "code", "pre", "a", "br"]
ALLOWED_ATTRS = {"a": ["href"]}

def ck_to_tg_html(html: str | None) -> str:
    if not html:
        return ""
    s = unescape(html)

    # 1) Параграфы/блоки → переносы строк
    s = re.sub(r'</(p|div|h[1-6])\s*>', "\n\n", s, flags=re.I)
    s = re.sub(r'<(p|div|h[1-6])[^>]*>', "", s, flags=re.I)

    # 2) Списки → «• » и переносы
    s = re.sub(r'</li\s*>', "\n", s, flags=re.I)
    s = re.sub(r'<li[^>]*>', "• ", s, flags=re.I)
    s = re.sub(r'</(ul|ol)\s*>', "\n", s, flags=re.I)
    s = re.sub(r'<(ul|ol)[^>]*>', "", s, flags=re.I)

    # 3) <br> → \n
    s = re.sub(r'<br\s*/?>', "\n", s, flags=re.I)

    # 4) &nbsp; → обычные пробелы
    s = s.replace("&nbsp;", " ").replace("\xa0", " ")

    # 5) Снести фигуры, спаны, таблицы и прочий несъедобный хлам
    s = re.sub(r'</?(span|figure|figcaption|table|thead|tbody|tfoot|tr|th|td)[^>]*>', "", s, flags=re.I)

    # 6) Чистим до разрешённого набора
    s = bleach.clean(s, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)

    # 7) Сжимаем лишние пустые строки (по желанию)
    s = re.sub(r'\n{3,}', "\n\n", s).strip()

    return s