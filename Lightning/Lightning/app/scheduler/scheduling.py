import logging
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from django.utils import timezone

from app.lightning.models.lightning_setting_models import LightningSetting
from app.scheduler.models.log_models import SchedulerLog


logger = logging.getLogger(__name__)


SLOT_WINDOW_MINUTES = 5

_scheduler_started = False


def start_scheduler():
    """Запускает APScheduler и ставит периодическую задачу-поллер.

    Важно: сам интервал опроса в БД (`poll_interval_minutes`) может меняться.
    Чтобы не перезапускать сервер, поллер запускается раз в 1 минуту,
    а внутренняя логика решает — выполнять ли проверку прямо сейчас.
    """
    global _scheduler_started
    if _scheduler_started:
        return
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            poll_lightning_schedule,
            trigger=IntervalTrigger(minutes=1), #имеет преимущество над Интервал повтора (часы) из админки
            id="lightning_poller",
            max_instances=1,
            replace_existing=True,
        )
        scheduler.start()
        _scheduler_started = True
    except Exception:
        logger.exception("APScheduler: ошибка запуска планировщика")


def _get_settings():
    try:
        return LightningSetting.objects.first()
    except Exception:
        logger.exception("Не удалось прочитать LightningSetting")
        return None


def _compute_today_slots(settings_obj, now_dt):
    """Возвращает список слотов запуска на сегодня с шагом schedule_interval_hours."""
    base = now_dt.replace(
        hour=settings_obj.schedule_start_hour, minute=0, second=0, microsecond=0
    )
    interval_hours = settings_obj.schedule_interval_hours or 24.0
    if interval_hours <= 0:
        interval_hours = 24.0

    slots = []
    slot = base
    end_of_day = base.replace(hour=23, minute=59, second=59, microsecond=999999)
    # Защита от слишком малого интервала: ограничим до 48 слотов в сутки
    while slot <= end_of_day and len(slots) < 48:
        slots.append(slot)
        slot = slot + timedelta(hours=interval_hours)
    return slots


def _format_slot_key(dt):
    return dt.strftime("%Y-%m-%dT%H:%M")


def _slot_already_handled(slot_key):
    """Проверяет, выполнялась ли рассылка для данного слота (running/completed).

    Не используем JSON-lookup по additional_info для совместимости
    с SQLite/MySQL без расширений. Проверяем ключ в Python.
    """
    try:
        since = timezone.now() - timedelta(days=2)
        logs = (
            SchedulerLog.objects.filter(
                task_name="send_unread_lightnings",
                start_time__gte=since,
            )
            .exclude(status="failed")
            .only("id", "additional_info")
        )
        for log in logs:
            info = log.additional_info or {}
            if isinstance(info, dict) and info.get("slot_key") == slot_key:
                return True
        return False
    except Exception:
        logger.exception("Ошибка проверки слота в SchedulerLog")
        return False


def _cleanup_old_logs(settings_obj):
    try:
        cutoff = timezone.now() - timedelta(days=settings_obj.cleanup_age_days)
        SchedulerLog.objects.filter(start_time__lt=cutoff).delete()
    except Exception:
        logger.exception("Ошибка очистки старых логов планировщика")


def poll_lightning_schedule():
    """Поллер: решает, пора ли запускать рассылку согласно настройкам.
    """
    now = timezone.localtime() if getattr(settings, "USE_TZ", False) else timezone.now()

    settings_obj = _get_settings()
    if not settings_obj:
        logger.info("poll: settings not found -> skip")
        return
    if not settings_obj.enable_scheduler:
        logger.info("poll: scheduler disabled -> skip")
        return

    # Гейт по частоте опроса: если текущая минута не кратна настройке — выходим
    poll_every = max(1, settings_obj.poll_interval_minutes)
    if now.minute % poll_every != 0:
        logger.debug(
            "poll: minute %s not aligned with poll_every=%s -> skip",
            now.minute,
            poll_every,
        )
        return

    # Регулярная очистка логов
    _cleanup_old_logs(settings_obj)

    # День недели активен?
    if now.weekday() not in settings_obj.active_days:
        logger.debug("poll: weekday %s not active -> skip", now.weekday())
        return

    # Находим ближайший прошедший слот за сегодня
    slots = _compute_today_slots(settings_obj, now)
    past_slots = [s for s in slots if s <= now]
    if not past_slots:
        logger.debug(
            "poll: no past slots for today from %s -> skip",
            _format_slot_key(slots[0]) if slots else "<no-slots>",
        )
        return
    slot_dt = past_slots[-1]
    slot_key = _format_slot_key(slot_dt)
    logger.info("poll: candidate slot %s", slot_key)

    # Если слот уже обрабатывали (running/completed) — выходим
    if _slot_already_handled(slot_key):
        logger.info("poll: slot %s already handled -> skip", slot_key)
        return

    # Фиксируем запуск в логе (running) с меткой слота
    log = SchedulerLog.objects.create(
        task_name="send_unread_lightnings",
        status="running",
        additional_info={"slot_key": slot_key},
    )
    logger.info("poll: started run for slot %s (log id=%s)", slot_key, log.id)

    started_at = timezone.now()
    total_messages_sent = 0
    total_errors = 0
    error_message = None

    try:
        # Здесь вызываем сервис рассылки (пока заглушка; будет реализован отдельно)
        from app.lightning.services.reminder_service import send_unread_lightnings

        result = send_unread_lightnings()
        total_messages_sent = int(result.get("total_messages_sent", 0))
        total_errors = int(result.get("total_errors", 0))
        status_val = "completed"
    except Exception as e:
        logger.exception("Ошибка выполнения рассылки молний")
        status_val = "failed"
        error_message = str(e)
    finally:
        try:
            exec_time = (timezone.now() - started_at).total_seconds()
            log.status = status_val
            log.end_time = timezone.now()
            log.execution_time = exec_time
            log.error_message = error_message
            log.total_messages_sent = total_messages_sent
            log.total_errors = total_errors
            if not log.additional_info:
                log.additional_info = {}
            log.additional_info["slot_key"] = slot_key
            log.save()
        except Exception:
            logger.exception("Ошибка при обновлении лога планировщика")
