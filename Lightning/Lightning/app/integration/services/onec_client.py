from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp


logger = logging.getLogger(__name__)


def build_onec_payload(
    *, last_name: str, name: str, birthday_iso: str
) -> Dict[str, Any]:
    """
    Формирует тело запроса к 1С для поиска сотрудника.

    Параметры:
    - last_name: фамилия сотрудника (кириллица, нормализовано FSM)
    - name: имя сотрудника (кириллица, нормализовано FSM)
    - birthday_iso: дата рождения в формате YYYY-MM-DD

    Замечания по контракту:
    - PHONE должен присутствовать как ключ, но отправляется пустой строкой
    - GUIDS отправляется пустым массивом
    - Ключи должны быть в верхнем регистре
    """
    return {
        "PHONE": "",
        "GUIDS": [],
        "LASTNAME": last_name,
        "NAME": name,
        "BIRTHDAY": birthday_iso,
    }


async def post_onec(
    *,
    url: str,
    username: str,
    password: str,
    payload: Dict[str, Any],
    timeout_seconds: float = 10.0,
) -> Optional[Dict[str, Any]]:
    """
    Выполняет POST-запрос к API 1С с BasicAuth.

    Возвращает:
    - dict с распарсенным JSON при успехе
    - None при сетевой/HTTP/парсинг ошибке

    Особенности:
    - Таймаут всего запроса 10с
    - Игнорируем некорректный Content-Type у 1С (content_type=None)
    - Фоллбэк на ручной json.loads из текстового ответа
    """
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    auth = aiohttp.BasicAuth(username, password)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url,
                json=payload,
                auth=auth,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error("Ошибка API 1С: %s - %s", resp.status, text)
                    return None
                try:
                    # Некоторые инстансы 1С возвращают неверный Content-Type
                    return await resp.json(content_type=None)
                except Exception:
                    text = await resp.text()
                    try:
                        import json as _json

                        return _json.loads(text)
                    except Exception:
                        logger.error("Не удалось распарсить JSON ответа 1С: %s", text)
                        return None
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.exception("Сбой запроса к 1С: %s", exc)
        return None
