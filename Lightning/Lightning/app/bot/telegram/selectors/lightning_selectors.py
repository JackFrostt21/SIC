from datetime import datetime
from django.db.models import Q
from django.utils import timezone
from asgiref.sync import sync_to_async

from app.lightning.models import (
    Lightning,
    LightningQuestion,
    LightningAnswer,
    LightningTest,
    LightningRead,
    UserTestAttempt,
)
from app.bot.models import TelegramUser, TelegramGroup


@sync_to_async
def get_user_by_telegram_id(telegram_id: int) -> TelegramUser | None:
    return TelegramUser.objects.filter(telegram_id=telegram_id).select_related(
        'job_title', 'department'
    ).first()
"""Подумать нужно ли еще загружать JobTitle и Department""" # TODO:


def q_lightning_access(user: TelegramUser) -> Q:
    """
    Условие (Q), по которому выбираются молнии, доступные пользователю:
      - указан конкретный user;
      - или одна из групп пользователя;
      - или совпадает должность;
      - или совпадает департамент.
    """
    # группы пользователя (через M2M в TelegramGroup)
    groups_qs = TelegramGroup.objects.filter(users__id=user.id).values_list('id', flat=True)

    q = (
        Q(user__id=user.id) |
        Q(group__id__in=groups_qs) |
        Q(job_titles=user.job_title) |
        Q(department=user.department)
    )
    return q

@sync_to_async
def list_relevant_lightnings(
    user_id: int,
    since: datetime | None = None,
) -> list[Lightning]:
    """
    Молнии, доступные пользователю, в порядке убывания даты создания
    """
    qs = Lightning.objects.filter(is_draft=False).distinct()

    user = TelegramUser.objects.select_related('job_title', 'department').get(id=user_id)
    qs = qs.filter(q_lightning_access(user))

    if since is not None:
        qs = qs.filter(created_at__gte=since)

    qs = qs.order_by('-created_at', '-id')
    return list(qs)


@sync_to_async
def list_unread_lightnings(
    user_id: int,
    since: datetime | None = None,
) -> list[Lightning]:
    """
    Непрочитанные/требующие действия молнии:
      - если молния БЕЗ вопросов → нет LightningRead(is_read=True)
      - если молния С вопросами → нет LightningTest(complete=True)
    """
    # доступные пользователю (не черновики + таргетинг + опционально с датой)
    available: list[Lightning] = list_relevant_lightnings.__wrapped__(user_id, since)
    if not available:
        return []

    ids = [l.id for l in available]

    # молнии, у которых есть хотя бы один вопрос (т.е. требуется тест)
    with_questions = set(
        LightningQuestion.objects
        .filter(lightning_id__in=ids)
        .values_list("lightning_id", flat=True)
        .distinct()
    )

    # успешно сданные тесты по этим молниям
    passed_ids = set(
        LightningTest.objects
        .filter(user_id=user_id, lightning_id__in=ids, complete=True)
        .values_list("lightning_id", flat=True)
    )

    # прочитанные молнии (для случаев без теста)
    read_ids = set(
        LightningRead.objects
        .filter(user_id=user_id, lightning_id__in=ids, is_read=True)
        .values_list("lightning_id", flat=True)
    )

    unread: list[Lightning] = []
    for l in available:
        if l.id in with_questions:
            # есть тест → "непрочитанная", пока тест не сдан
            if l.id not in passed_ids:
                unread.append(l)
        else:
            # теста нет → "непрочитанная", пока не помечена как прочитанная
            if l.id not in read_ids:
                unread.append(l)

    return unread


@sync_to_async
def get_lightning(lightning_id: int) -> Lightning | None:
    return Lightning.objects.filter(id=lightning_id, is_draft=False).first()


# ---------- Вопросы/ответы ----------

@sync_to_async
def list_questions(lightning_id: int) -> list[LightningQuestion]:
    return list(
        LightningQuestion.objects.filter(lightning_id=lightning_id).order_by('order', 'id')
    )

@sync_to_async
def list_answers(question_id: int) -> list[LightningAnswer]:
    return list(
        LightningAnswer.objects.filter(question_id=question_id).order_by('order', 'id')
    )


# ---------- Чтение статусов/тестовых записей (только чтение!) ----------

@sync_to_async
def get_read_record(user_id: int, lightning_id: int) -> LightningRead | None:
    return LightningRead.objects.filter(user_id=user_id, lightning_id=lightning_id).first()

@sync_to_async
def get_test_record(user_id: int, lightning_id: int) -> LightningTest | None:
    return LightningTest.objects.filter(user_id=user_id, lightning_id=lightning_id).first()

@sync_to_async
def get_attempt_record(user_id: int, lightning_id: int) -> UserTestAttempt | None:
    return UserTestAttempt.objects.filter(telegramuser_id=user_id, lightning_id=lightning_id).first()


# ---------- Утилиты ----------

@sync_to_async
def get_min_pass_percent(lightning_id: int) -> int:
    obj = Lightning.objects.only('id', 'min_test_percent_course').get(id=lightning_id)
    return int(obj.min_test_percent_course)


@sync_to_async
def get_correct_answer_ids(question_id: int) -> list[int]:
    return list(
        LightningAnswer.objects.filter(question_id=question_id, is_correct=True)
        .values_list('id', flat=True)
    )

# за один запрос соберёт для набора молний: есть ли у молнии вопросы, и считается ли она “закрытой” для пользователя (прочитал если без теста / сдал если есть тест).
@sync_to_async
def get_lightnings_status(user_id: int, lightning_ids: list[int]) -> dict[int, dict]:
    """
    Возвращает статус прохождения молний для пользователя:
      { lightning_id: {"has_questions": bool, "is_completed": bool} }
    
    Статус:
      - для молний с вопросами: тест пройден (complete=True в LightningTest)
      - для молний без вопросов: материал прочитан (is_read=True в LightningRead)
    """
    if not lightning_ids:
        return {}

    # Молнии, у которых есть вопросы
    lightnings_with_questions = set(
        LightningQuestion.objects
        .filter(lightning_id__in=lightning_ids)
        .values_list("lightning_id", flat=True)
        .distinct()
    )
    # Молнии, где пользователь прошел тест
    completed_tests = set(
        LightningTest.objects
        .filter(user_id=user_id, lightning_id__in=lightning_ids, complete=True)
        .values_list("lightning_id", flat=True)
    )
    # Молнии, где пользователь прочитал материал
    read_materials = set(
        LightningRead.objects
        .filter(user_id=user_id, lightning_id__in=lightning_ids, is_read=True)
        .values_list("lightning_id", flat=True)
    )

    status: dict[int, dict] = {}
    for lightning_id in lightning_ids:
        # Проверяем: есть ли у этой молнии вопросы?
        has_questions = lightning_id in lightnings_with_questions

        if has_questions:
            # Если есть вопросы: проверяем, прошел ли тест
            is_completed = lightning_id in completed_tests
        else:
            # Если нет вопросов: проверяем, прочитал ли материал
            is_completed = lightning_id in read_materials

        status[lightning_id] = {
            "has_questions": has_questions, 
            "is_completed": is_completed
        }
    return status