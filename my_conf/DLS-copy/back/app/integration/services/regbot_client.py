from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp


logger = logging.getLogger(__name__)


def build_regbot_telegram_payload(*, telegram_id: int) -> Dict[str, Any]:
    """Формирует тело запроса к RegBot для поиска по Telegram ID."""
    return {
        "TELEGRAM_ID": telegram_id,
    }


def build_regbot_employee_payload(
    *, telegram_id: int, last_name: str, name: str, birthday_iso: str
) -> Dict[str, Any]:
    """Формирует тело запроса к RegBot для поиска по ФИО + ДР."""
    return {
        "TELEGRAM_ID": telegram_id,
        "PHONE": "",
        "GUIDS": [],
        "LASTNAME": last_name,
        "NAME": name,
        "BIRTHDAY": birthday_iso,
    }


async def post_regbot(
    *,
    url: str,
    payload: Dict[str, Any],
    api_key: Optional[str] = None,
    timeout_seconds: float = 10.0,
) -> Dict[str, Any]:
    """
    Выполняет POST-запрос к RegBot и возвращает нормализованный результат.

    Результат:
    - http_status: int | None
    - status: str | None
    - data: Any
    - body: dict | None
    - error: str | None
    """
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if api_key:
        headers["X-API-Key"] = api_key

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                body: Optional[Dict[str, Any]] = None

                try:
                    parsed = await resp.json(content_type=None)
                    if isinstance(parsed, dict):
                        body = parsed
                except Exception:
                    text = await resp.text()
                    logger.error("Не удалось распарсить JSON ответа RegBot: %s", text)

                return {
                    "http_status": resp.status,
                    "status": (body or {}).get("status"),
                    "data": (body or {}).get("data"),
                    "body": body,
                    "error": None,
                }
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.exception("Сбой запроса к RegBot: %s", exc)
        return {
            "http_status": None,
            "status": None,
            "data": None,
            "body": None,
            "error": str(exc),
        }
