from django.contrib import admin
from django.contrib import messages
from django_object_actions import DjangoObjectActions
from django.conf import settings
from asgiref.sync import sync_to_async
import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramRetryAfter,
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramNetworkError,
)
from app.bot.telegram.keyboards.lightning_kb import get_lightnings_list_kb
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.formats.base_formats import XLSX, XLS, CSV
from .resources import (
    LightningResource,
    LightningQuestionResource,
    LightningAnswerResource,
    LightningReadResource,
    LightningTestResource,
)

from .models import (
    Lightning,
    LightningQuestion,
    LightningAnswer,
    UserTestAttempt,
    LightningSetting,
    LightningRead,
    LightningTest,
)


class LightningQuestionInline(admin.TabularInline):
    model = LightningQuestion
    fields = ("name", "is_multiple_choice", "order")
    extra = 0
    show_change_link = True


class LightningAnswerInline(admin.TabularInline):
    model = LightningAnswer
    fields = ("text", "is_correct", "order")
    extra = 0


@admin.register(Lightning)
class LightningAdmin(DjangoObjectActions, ImportExportModelAdmin):
    resource_class = LightningResource
    formats = (XLSX, XLS, CSV)

    list_display = (
        "name",
        "is_draft",
        "created_at",
        "min_test_percent_course",
        "users_count",
        "questions_count",
    )
    list_filter = ("is_draft", "created_at")
    search_fields = ("name", "content")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    inlines = (LightningQuestionInline,)
    filter_horizontal = ("user", "group", "job_titles", "department")
    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Основное",
            {
                "fields": ("is_draft", "name", "created_at", "min_test_percent_course"),
            },
        ),
        (
            "Аудитория",
            {
                "fields": ("user", "group", "job_titles", "department"),
                "description": "Назначение молнии пользователям, группам, должностям, подразделениям",
            },
        ),
        (
            "Контент",
            {
                "fields": ("content", "image", "file"),
            },
        ),
    )

    # --- Object action: Отправить молнию
    change_actions = ("send_lightning_action",)

    def send_lightning_action(self, request, obj):
        # Запускаем асинхронную рассылку из синхронного экшена
        try:
            asyncio.run(self._send_lightning_async(request, obj))
        except RuntimeError:
            # На случай, если уже есть активный цикл событий
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(self._send_lightning_async(request, obj))
            finally:
                loop.close()

    send_lightning_action.label = "⚡ Отправить молнию"
    send_lightning_action.short_description = "Отправить молнию выбранной аудитории"
    send_lightning_action.attrs = {"class": "btn btn-dark btn-sm btn-block"}

    @admin.display(description="Пользователи")
    def users_count(self, obj):
        from app.bot.models.telegramuser_models import TelegramUser

        base_filter = {
            "state": 1,
            "telegram_id__isnull": False,
            "telegram_id__gt": 0,
        }

        user_ids = set(obj.user.filter(**base_filter).values_list("id", flat=True))

        group_ids = list(obj.group.values_list("id", flat=True))
        if group_ids:
            group_user_ids = TelegramUser.objects.filter(
                groups__id__in=group_ids,
                **base_filter,
            ).values_list("id", flat=True)
            user_ids.update(group_user_ids)

        job_title_ids = list(obj.job_titles.values_list("id", flat=True))
        if job_title_ids:
            job_user_ids = TelegramUser.objects.filter(
                job_title_id__in=job_title_ids,
                **base_filter,
            ).values_list("id", flat=True)
            user_ids.update(job_user_ids)

        department_ids = list(obj.department.values_list("id", flat=True))
        if department_ids:
            department_user_ids = TelegramUser.objects.filter(
                department_id__in=department_ids,
                **base_filter,
            ).values_list("id", flat=True)
            user_ids.update(department_user_ids)

        return len(user_ids)

    @admin.display(description="Вопросы")
    def questions_count(self, obj):
        return obj.questions.count()

    # ------------------------
    # Вспомогательная логика отправки
    # ------------------------
    async def _send_lightning_async(self, request, lightning_obj):
        sent = 0
        failed = 0

        # Локальный краткоживущий бот: безопасно для вызовов из админки
        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        try:
            # Импорты моделей внутри, чтобы избежать циклов
            from app.bot.models.telegramuser_models import TelegramUser
            from app.lightning.models.lightning_data_models import LightningRead
            from app.lightning.models.lightning_models import Lightning

            # Запрет отправки черновиков
            if getattr(lightning_obj, "is_draft", False):
                self.message_user(
                    request,
                    "Нельзя отправить черновик. Снимите флаг 'Черновик' перед отправкой.",
                    level=messages.WARNING,
                )
                return

            # Получаем глобальные настройки для отправки GIF
            settings_obj = await sync_to_async(LightningSetting.objects.first)()
            enable_gif = (
                bool(getattr(settings_obj, "enable_gif", False))
                if settings_obj
                else False
            )
            gif_path = (
                settings_obj.gif.path if settings_obj and settings_obj.gif else None
            )

            # 1) Собираем аудиторию (пользователи, группы, должности, подразделения)
            async def collect_users():
                def _collect():
                    users_set = set()
                    # Прямые пользователи
                    for u in lightning_obj.user.all():
                        users_set.add(u)
                    # Из групп
                    for g in lightning_obj.group.all():
                        for u in g.users.all():
                            users_set.add(u)
                    # По должностям
                    jt_ids = list(lightning_obj.job_titles.values_list("id", flat=True))
                    if jt_ids:
                        for u in TelegramUser.objects.filter(job_title_id__in=jt_ids):
                            users_set.add(u)
                    # По подразделениям
                    dep_ids = list(
                        lightning_obj.department.values_list("id", flat=True)
                    )
                    if dep_ids:
                        for u in TelegramUser.objects.filter(department_id__in=dep_ids):
                            users_set.add(u)

                    # Фильтруем только активных с валидным telegram_id
                    users_list = []
                    for u in users_set:
                        try:
                            if (
                                getattr(u, "state", 1) == 1
                                and getattr(u, "telegram_id", 0)
                                and u.telegram_id > 0
                            ):
                                users_list.append(u)
                        except Exception:
                            continue
                    return users_list

                return await sync_to_async(_collect)()

            users = await collect_users()

            # 2) Для каждого пользователя: гарантируем запись LightningRead и отправляем только текущую молнию
            async def ensure_lr_and_unread(user):
                def _ensure_and_get():
                    # Создаём запись для текущей молнии, если её ещё нет
                    LightningRead.objects.get_or_create(
                        user=user,
                        lightning=lightning_obj,
                        defaults={"is_read": False},
                    )
                    # Блок формирования списка всех непрочитанных временно отключён:
                    # unread_ids = LightningRead.objects.filter(
                    #     user=user, is_read=False, lightning__is_draft=False
                    # ).values_list("lightning_id", flat=True)
                    # return list(
                    #     Lightning.objects.filter(
                    #         id__in=unread_ids, is_draft=False
                    #     ).order_by("-created_at")
                    # )
                    # Возвращаем только текущую молнию
                    return [lightning_obj]

                return await sync_to_async(_ensure_and_get)()

            for user in users:
                try:
                    unread_lightnings = await ensure_lr_and_unread(user)

                    if unread_lightnings:
                        # При включенной настройке и наличии файла отправляем GIF перед текстом
                        if enable_gif and gif_path:
                            try:
                                from aiogram.types import FSInputFile

                                await bot.send_animation(
                                    chat_id=user.telegram_id,
                                    animation=FSInputFile(gif_path),
                                )
                                await asyncio.sleep(0.02)
                            except Exception:
                                # Не блокируем основную отправку из-за GIF
                                pass

                        kb = get_lightnings_list_kb(unread_lightnings, status=None)
                        text = "Вам поступили новые молнии. Ознакомьтесь, нажав на соответствующую кнопку:"
                        await bot.send_message(user.telegram_id, text, reply_markup=kb)
                    else:
                        pass

                    sent += 1
                    await asyncio.sleep(
                        0.05
                    )  # TODO подумать над задержкой, ранее была 1 для обхода блокировки
                except TelegramRetryAfter as e:
                    await asyncio.sleep(getattr(e, "retry_after", 1))
                    failed += 1
                except TelegramForbiddenError:
                    failed += 1
                except (TelegramBadRequest, TelegramNetworkError):
                    failed += 1
                except Exception:
                    failed += 1

            # 3) Сообщаем итоги админ-пользователю
            self.message_user(
                request,
                f"Отправка завершена. Успешно: {sent}, ошибок: {failed}.",
                level=messages.INFO,
            )
        finally:
            try:
                await bot.session.close()
            except Exception:
                pass


@admin.register(LightningQuestion)
class LightningQuestionAdmin(ImportExportModelAdmin):
    resource_class = LightningQuestionResource
    formats = (XLSX, XLS, CSV)

    list_display = ("name", "lightning", "is_multiple_choice", "order")
    list_filter = ("lightning", "is_multiple_choice")
    search_fields = ("name", "lightning__name")
    ordering = ("lightning__name", "order")

    inlines = (LightningAnswerInline,)
    autocomplete_fields = ("lightning",)


@admin.register(LightningAnswer)
class LightningAnswerAdmin(ImportExportModelAdmin):
    resource_class = LightningAnswerResource
    formats = (XLSX, XLS, CSV)

    list_display = ("text", "question", "is_correct", "order")
    list_filter = ("is_correct", "question__lightning")
    search_fields = ("text", "question__name", "question__lightning__name")
    ordering = ("question__lightning__name", "question__order", "order")

    autocomplete_fields = ("question",)


@admin.register(UserTestAttempt)
class UserTestAttemptAdmin(admin.ModelAdmin):
    list_display = ("telegramuser", "lightning", "attempts", "updated_at")
    list_filter = ("updated_at", "lightning")
    search_fields = (
        "telegramuser__telegram_id",
        "telegramuser__username",
        "telegramuser__full_name",
        "lightning__name",
    )
    ordering = ("-updated_at",)
    raw_id_fields = ("telegramuser", "lightning")


@admin.register(LightningRead)
class LightningReadAdmin(ImportExportModelAdmin):
    resource_class = LightningReadResource
    formats = (XLSX, XLS, CSV)

    list_display = ("user", "lightning", "is_read", "created_at", "updated_at")
    list_filter = ("is_read", "created_at", "updated_at", "lightning")
    search_fields = (
        "user__telegram_id",
        "user__username",
        "user__full_name",
        "lightning__name",
    )
    ordering = ("-updated_at",)
    raw_id_fields = ("user", "lightning")


@admin.register(LightningTest)
class LightningTestAdmin(ImportExportModelAdmin):
    resource_class = LightningTestResource
    formats = (XLSX, XLS, CSV)

    list_display = (
        "user",
        "lightning",
        "complete",
        "quantity_correct",
        "quantity_not_correct",
        "created_at",
        "updated_at",
    )
    list_filter = ("complete", "created_at", "lightning")
    search_fields = (
        "user__telegram_id",
        "user__username",
        "user__full_name",
        "lightning__name",
    )
    ordering = ("-created_at",)
    raw_id_fields = ("user", "lightning")


@admin.register(LightningSetting)
class LightningSettingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "enable_scheduler",
        "schedule_start_hour",
        "schedule_interval_hours",
        "poll_interval_minutes",
        "batch_size",
    )
    list_filter = (
        "enable_scheduler",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    search_fields = ("name",)
    ordering = ("name",)

    fieldsets = (
        (
            "Общее",
            {
                "fields": ("name", "gif"),
            },
        ),
        (
            "Планировщик",
            {
                "fields": (
                    "enable_scheduler",
                    "schedule_start_hour",
                    "schedule_interval_hours",
                    "poll_interval_minutes",
                ),
            },
        ),
        (
            "Дни недели",
            {
                "fields": (
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ),
            },
        ),
        (
            "Отправка",
            {
                "fields": (
                    "batch_size",
                    "delay_between_users",
                    "delay_between_batches",
                    "max_retry_attempts",
                    "enable_gif",
                ),
            },
        ),
        (
            "Очистка",
            {
                "fields": ("cleanup_age_days",),
            },
        ),
    )
