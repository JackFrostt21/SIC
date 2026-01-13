import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
)
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render
from django.template import context

from app.bot.models.telegramuser_models import TelegramUser  # , TelegramGroup
from app.bot.telegram.keyboards.lightning_kb import get_lightnings_list_kb
from app.lightning.models import LightningSetting
from app.lightning.models.lightning_models import Lightning
from app.lightning.models.lightning_data_models import LightningRead

# from app.organization.models.company_models import Department, JobTitle


def send_lightnings_to_users(lightnings, users):
    # Готовим статистику выполнения, чтобы показать результат в интерфейсе.
    stats = {
        "created": 0,
        "sent": 0,
        "skipped": 0,
        "errors": 0,
    }

    # Отбрасываем черновики, чтобы не отправлять неподготовленные молнии.
    valid_lightnings = [l for l in lightnings if not getattr(l, "is_draft", False)]
    if not valid_lightnings:
        return stats

    # Отбираем пользователей только с валидным telegram_id.
    valid_users = [
        u
        for u in users
        if getattr(u, "telegram_id", 0) and getattr(u, "telegram_id", 0) > 0
    ]
    if not valid_users:
        return stats

    async def _send():
        # Создаём бота на время рассылки.
        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        try:
            # Читаем настройки для GIF и прочих опций отправки.
            settings_obj = await sync_to_async(LightningSetting.objects.first)()
            enable_gif = (
                bool(getattr(settings_obj, "enable_gif", False))
                if settings_obj
                else False
            )
            gif_path = (
                settings_obj.gif.path if settings_obj and settings_obj.gif else None
            )

            # Проходим по каждому пользователю и всем выбранным молниям.
            for user in valid_users:
                try:
                    # Создаём записи LightningRead для каждой молнии.
                    for lightning in valid_lightnings:
                        await sync_to_async(LightningRead.objects.get_or_create)(
                            user=user,
                            lightning=lightning,
                            defaults={"is_read": False},
                        )
                        stats["created"] += 1

                    # Опционально отправляем GIF, если разрешено в настройках.
                    if enable_gif and gif_path:
                        try:
                            await bot.send_animation(
                                chat_id=user.telegram_id,
                                animation=FSInputFile(gif_path),
                            )
                        except Exception:
                            stats["errors"] += 1

                    # Формируем клавиатуру и текст уведомления.
                    kb = get_lightnings_list_kb(valid_lightnings, status=None)
                    text = (
                        "Вам поступили новые молнии. Ознакомьтесь, нажав на "
                        "соответствующую кнопку:"
                    )

                    # Отправляем сообщение пользователю.
                    await bot.send_message(
                        user.telegram_id,
                        text,
                        reply_markup=kb,
                    )
                    stats["sent"] += 1

                    # Небольшая задержка, чтобы не улететь в лимиты.
                    await asyncio.sleep(0.05)

                except TelegramRetryAfter as e:
                    await asyncio.sleep(getattr(e, "retry_after", 1))
                    stats["errors"] += 1
                except (
                    TelegramForbiddenError,
                    TelegramBadRequest,
                    TelegramNetworkError,
                ):
                    stats["errors"] += 1
                except Exception:
                    stats["errors"] += 1
        finally:
            # Закрываем сессию бота корректно.
            try:
                await bot.session.close()
            except Exception:
                pass

    # Запускаем асинхронную отправку из синхронного кода.
    try:
        asyncio.run(_send())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_send())
        finally:
            loop.close()

    return stats


def lightning_multisend_view(request):
    # Параметры поиска по молниям и пользователям (GET).
    lightning_search = request.GET.get("lsearch", "").strip()
    user_search = request.GET.get("usearch", "").strip()

    # Базовые QuerySet с применением поиска и сортировки.
    lightning_qs = (
        Lightning.objects.filter(is_draft=False)
        .only("name", "created_at")
        .order_by("-created_at")
    )
    if lightning_search:
        lightning_qs = lightning_qs.filter(name__icontains=lightning_search)

    telegramuser_qs = (
        TelegramUser.objects.filter(state=TelegramUser.STATE_ACTIVE)
        .only("full_name")
        .order_by("full_name")
    )
    if user_search:
        telegramuser_qs = telegramuser_qs.filter(full_name__icontains=user_search)

    # Обрабатываем отправку при POST: берём выбранные id и запускаем логику.
    if request.method == "POST":
        lightning_ids = request.POST.getlist("lightning_ids")
        user_ids = request.POST.getlist("user_ids")

        selected_lightnings = lightning_qs.filter(id__in=lightning_ids)
        selected_users = telegramuser_qs.filter(
            id__in=user_ids,
            telegram_id__isnull=False,
            telegram_id__gt=0,
        )

        if not selected_lightnings.exists():
            messages.warning(request, "Выберите хотя бы одну молнию.")
        elif not selected_users.exists():
            messages.warning(request, "Выберите хотя бы одного пользователя.")
        else:
            stats = send_lightnings_to_users(
                list(selected_lightnings),
                list(selected_users),
            )
            messages.success(
                request,
                (
                    f"Создано связок: {stats['created']}; "
                    f"отправлено пользователям: {stats['sent']}; "
                    f"пропущено: {stats['skipped']}; "
                    f"ошибок: {stats['errors']}."
                ),
            )

    # Готовим страницы по 7 и 10 элементов соответственно.
    lightning_page = Paginator(lightning_qs, 7).get_page(request.GET.get("lpage"))
    telegramuser_page = Paginator(telegramuser_qs, 7).get_page(
        request.GET.get("upage")
    )

    # Контекст для шаблона.
    context = {
        "lightning_page": lightning_page,
        "telegramuser_page": telegramuser_page,
        "lightning_search": lightning_search,
        "user_search": user_search,
    }

    return render(
        request,
        "lightning_multisend.html",
        context,
    )
