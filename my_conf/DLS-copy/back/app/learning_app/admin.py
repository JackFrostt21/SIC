from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.conf import settings
import asyncio
from aiogram import Bot
from .models import (
    TagCourse,
    CourseDirection,
    TrainingCourse,
    CourseTopic,
    TopicQuestion,
    AnswerOption,
    Certificate,
    RatingTrainingCourse,
    CourseDeadline,
    NewsBlock,
    UserNewsStatus,
    ScormPack,
    ObligatoryList,
    CourseAssignmentNotification,
)
from app.bot.models import SubscriptionUser


class TopicQuestionInline(admin.TabularInline):
    model = TopicQuestion
    extra = 0
    fields = ("title", "is_multiple_choice", "order", "is_actual", "more_info")
    readonly_fields = ("more_info",)
    show_change_link = True


class TopicQuestionInlineForCourse(admin.TabularInline):
    model = TopicQuestion
    fk_name = "training"
    extra = 0
    fields = ("title", "course_topic", "is_multiple_choice", "order", "is_actual", "more_info")
    readonly_fields = ("more_info",)
    show_change_link = True


@admin.register(TagCourse)
class TagCourseAdmin(admin.ModelAdmin):
    list_display = ("tag_name", "is_actual")
    search_fields = ("tag_name",)
    list_filter = ("is_actual",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(CourseDirection)
class CourseDirectionAdmin(admin.ModelAdmin):
    list_display = ("title", "is_actual")
    search_fields = ("title",)
    list_filter = ("is_actual",)
    readonly_fields = ("created_at", "updated_at")


class CourseTopicInline(admin.TabularInline):
    model = CourseTopic
    extra = 0
    fields = ("title", "is_actual", "more_info")
    readonly_fields = ("more_info",)
    show_change_link = True


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "title",
        "course_direction",
        "archive",
        "open_course",
        "notification_sent",
        "is_actual",
        "min_test_percent_course",
        "users_count",
    )
    list_filter = (
        "archive",
        "is_actual",
        "obligatory",
        "open_course",
        "notification_sent",
        "course_direction",
        "tag",
    )
    search_fields = ("title", "description", "author")
    filter_horizontal = ("tag", "user", "group")
    inlines = [CourseTopicInline, TopicQuestionInlineForCourse]
    readonly_fields = ("created_at", "updated_at", "display_image")
    actions = ["send_course_notifications", "notify_assigned_users"]
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "description",
                    "author",
                    "archive",
                    "is_actual",
                    "obligatory",
                    "open_course",
                    "notification_sent",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Настройки курса",
            {
                "fields": (
                    "course_direction",
                    "tag",
                    "min_test_percent_course",
                    "certificate_validity_days",
                    "image_course",
                    "display_image",
                )
            },
        ),
        ("Доступ", {"fields": ("user", "group")}),
    )

    def image_preview(self, obj):
        if obj.image_course:
            return mark_safe(
                f'<img src="{obj.image_course.url}" width="50" height="30" style="object-fit: cover; border-radius: 4px;" />'
            )
        return mark_safe(
            '<div style="width: 50px; height: 30px; background-color: #f0f0f0; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #666;">Нет</div>'
        )

    image_preview.short_description = "Изображение"

    def users_count(self, obj):
        # Собираем ID пользователей, напрямую назначенных на курс
        user_ids = set(obj.user.values_list("pk", flat=True))
        # Проходим по всем группам курса и добавляем их участников
        for group in obj.group.all():
            user_ids.update(group.users.values_list("pk", flat=True))
        return len(user_ids)

    users_count.short_description = "Кол-во студентов"

    def display_image(self, obj):
        if obj.image_course:
            return mark_safe(f'<img src="{obj.image_course.url}" width="50" />')
        return "Нет изображения"

    display_image.short_description = "Предпросмотр"

    def send_course_notifications(self, request, queryset):
        """
        Admin action для отправки уведомлений о новых курсах подписчикам
        """
        # Фильтруем только открытые курсы, которым еще не отправлялись уведомления
        courses_to_notify = queryset.filter(
            open_course=True, notification_sent=False, is_actual=True
        )

        if not courses_to_notify.exists():
            self.message_user(
                request,
                "Не найдено подходящих курсов для отправки уведомлений. "
                "Курсы должны быть открытыми, актуальными и без отправленных уведомлений.",
                level=messages.WARNING,
            )
            return

        # Получаем всех подписчиков
        subscribers = SubscriptionUser.objects.all()

        if not subscribers.exists():
            self.message_user(
                request,
                "Нет подписчиков на уведомления о новых курсах.",
                level=messages.WARNING,
            )
            return

        # ВАЖНО: Получаем данные из БД ДО запуска асинхронной функции
        # Преобразуем QuerySet в список словарей с нужными данными
        courses_data = []
        for course in courses_to_notify:
            courses_data.append(
                {
                    "id": course.id,
                    "title": course.title,
                    "description": course.description or "",
                }
            )

        # Получаем список telegram_id всех подписчиков
        subscriber_ids = list(subscribers.values_list("telegram_id", flat=True))

        # Запускаем асинхронную отправку уведомлений
        try:
            sent_count = asyncio.run(
                self._send_notifications_async(courses_data, subscriber_ids)
            )

            # Помечаем курсы как отправленные
            courses_to_notify.update(notification_sent=True)

            self.message_user(
                request,
                f"✅ Успешно! Уведомления о {len(courses_data)} курсе(ах) "
                f"отправлены {sent_count} подписчику(ам).",
                level=messages.SUCCESS,
            )

        except Exception as e:
            self.message_user(
                request,
                f"❌ Ошибка при отправке уведомлений: {e}",
                level=messages.ERROR,
            )

    send_course_notifications.short_description = (
        "📢 Отправить уведомление о новых курсах"
    )

    async def _send_notifications_async(self, courses_data, subscriber_ids):
        """
        Асинхронная функция для отправки уведомлений через Telegram Bot

        :param courses_data: Список словарей с данными курсов [{'id': 1, 'title': '...', 'description': '...'}, ...]
        :param subscriber_ids: Список telegram_id подписчиков [123456, 789012, ...]
        """
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        sent_count = 0

        # Формируем список курсов для сообщения
        courses_list = []
        for course in courses_data:
            courses_list.append(f"📚 <b>{course['title']}</b>")
            if course["description"]:
                # Ограничиваем описание 150 символами
                desc = (
                    course["description"][:150] + "..."
                    if len(course["description"]) > 150
                    else course["description"]
                )
                courses_list.append(f"   {desc}")

        courses_text = "\n\n".join(courses_list)

        # Формируем итоговое сообщение
        if len(courses_data) == 1:
            message_text = (
                "🎉 <b>Доступна новая открытая программа обучения!</b>\n\n"
                f"{courses_text}\n\n"
                "Для добавления нового курса Перейдите в раздел '✏️ Самозапись на курсы' чтобы добавить программу в список доступных!"
            )
        else:
            message_text = (
                f"🎉 <b>Доступно {len(courses_data)} новых открытых программ обучения!</b>\n\n"
                f"{courses_text}\n\n"
                "Для добавления нового курса Перейдите в раздел '✏️ Самозапись на курсы' чтобы добавить программу в список доступных!"
            )

        # Отправляем сообщения всем подписчикам
        for telegram_id in subscriber_ids:
            try:
                await bot.send_message(
                    chat_id=telegram_id, text=message_text, parse_mode="HTML"
                )
                sent_count += 1
            except Exception as e:
                # Логируем ошибку, но продолжаем отправку остальным
                print(f"Ошибка отправки уведомления пользователю {telegram_id}: {e}")

        # Закрываем сессию бота
        await bot.session.close()

        return sent_count

    def notify_assigned_users(self, request, queryset):
        """
        Admin action для отправки уведомлений пользователям о назначении курса
        """
        if queryset.count() > 1:
            self.message_user(
                request,
                "⚠️ Выберите только один курс для отправки уведомлений.",
                level=messages.WARNING,
            )
            return

        course = queryset.first()

        # Собираем всех назначенных пользователей
        # 1. Пользователи, назначенные напрямую
        assigned_users_ids = set(course.user.values_list("id", flat=True))

        # 2. Пользователи из групп
        for group in course.group.all():
            assigned_users_ids.update(group.users.values_list("id", flat=True))

        if not assigned_users_ids:
            self.message_user(
                request,
                "⚠️ Для этого курса не назначено ни одного пользователя или группы.",
                level=messages.WARNING,
            )
            return

        # Получаем пользователей, которые уже получили уведомление
        already_notified_ids = set(
            CourseAssignmentNotification.objects.filter(
                training_course=course, user_id__in=assigned_users_ids
            ).values_list("user_id", flat=True)
        )

        # Находим пользователей, которым нужно отправить уведомление
        users_to_notify_ids = assigned_users_ids - already_notified_ids

        if not users_to_notify_ids:
            self.message_user(
                request,
                f"ℹ️ Все назначенные пользователи ({len(assigned_users_ids)}) уже получили уведомление о курсе.",
                level=messages.INFO,
            )
            return

        # Получаем данные пользователей для отправки
        from app.bot.models import TelegramUser

        users_to_notify = TelegramUser.objects.filter(id__in=users_to_notify_ids)

        # Подготавливаем данные для асинхронной отправки
        users_data = []
        for user in users_to_notify:
            users_data.append(
                {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "name": user.full_name
                    or user.user_name
                    or f"ID: {user.telegram_id}",
                }
            )

        course_data = {
            "id": course.id,
            "title": course.title,
            "description": course.description or "",
        }

        # Запускаем асинхронную отправку
        try:
            sent_count = asyncio.run(
                self._send_assignment_notifications_async(course_data, users_data)
            )

            # Создаем записи о рассылке
            notifications_to_create = [
                CourseAssignmentNotification(
                    training_course=course, user_id=user_data["id"]
                )
                for user_data in users_data
                if sent_count > 0  # Создаем только если хоть кому-то отправилось
            ]

            if notifications_to_create:
                CourseAssignmentNotification.objects.bulk_create(
                    notifications_to_create, ignore_conflicts=True
                )

            self.message_user(
                request,
                f"✅ Успешно! Уведомление о назначении курса отправлено {sent_count} "
                f"из {len(users_data)} пользователю(ям). "
                f"Уже получали уведомление ранее: {len(already_notified_ids)}.",
                level=messages.SUCCESS,
            )

        except Exception as e:
            self.message_user(
                request,
                f"❌ Ошибка при отправке уведомлений: {e}",
                level=messages.ERROR,
            )

    notify_assigned_users.short_description = "📧 Уведомить назначенных пользователей"

    async def _send_assignment_notifications_async(self, course_data, users_data):
        """
        Асинхронная функция для отправки уведомлений о назначении курса

        :param course_data: Словарь с данными курса {'id': 1, 'title': '...', 'description': '...'}
        :param users_data: Список словарей с данными пользователей [{'id': 1, 'telegram_id': 123, 'name': '...'}, ...]
        """
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        sent_count = 0

        # Формируем сообщение
        message_text = f"📚 <b>Вам назначен курс</b>\n\n<b>{course_data['title']}</b>\n"

        if course_data["description"]:
            # Ограничиваем описание 200 символами
            desc = (
                course_data["description"][:200] + "..."
                if len(course_data["description"]) > 200
                else course_data["description"]
            )
            message_text += f"\n{desc}\n"

        message_text += (
            "\n💡 Перейдите в раздел '📚 Программы обучения' чтобы начать обучение!"
        )

        # Отправляем сообщения всем пользователям
        for user_data in users_data:
            try:
                await bot.send_message(
                    chat_id=user_data["telegram_id"],
                    text=message_text,
                    parse_mode="HTML",
                )
                sent_count += 1
            except Exception as e:
                # Логируем ошибку, но продолжаем отправку остальным
                print(
                    f"Ошибка отправки уведомления пользователю {user_data['name']} "
                    f"(telegram_id: {user_data['telegram_id']}): {e}"
                )

        # Закрываем сессию бота
        await bot.session.close()

        return sent_count


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 1
    fields = ("order", "text", "is_correct", "is_actual")


@admin.register(CourseTopic)
class CourseTopicAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "title",
        "training_course",
        "has_content",
        "is_actual",
    )
    list_filter = (
        "is_actual",
        "training_course",
        "main_text_readuser",
        "pdf_file_readuser",
    )
    search_fields = ("title", "description", "main_text")
    readonly_fields = ("created_at", "updated_at", "display_image")
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "training_course",
                    "order",
                    "title",
                    "description",
                    "is_actual",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Основной контент",
            {"fields": ("main_text", "image_course_topic", "display_image")},
        ),
        (
            "Файлы и медиа",
            {
                "classes": ("collapse",),
                "fields": ("pdf_file", "audio_file", "video_file"),
            },
        ),
        (
            "Настройки отображения в боте",
            {
                "classes": ("collapse",),
                "fields": (
                    "main_text_readuser",
                    "main_text_webapp_readuser",
                    "pdf_file_readuser",
                    "audio_file_readuser",
                    "video_file_readuser",
                ),
            },
        ),
    )
    inlines = [TopicQuestionInline]

    def image_preview(self, obj):
        if obj.image_course_topic:
            return mark_safe(
                f'<img src="{obj.image_course_topic.url}" width="50" height="30" style="object-fit: cover; border-radius: 4px;" />'
            )
        return mark_safe(
            '<div style="width: 50px; height: 30px; background-color: #f0f0f0; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #666;">Нет</div>'
        )

    image_preview.short_description = "Изображение"

    def has_content(self, obj):
        has_main = obj.has_main_text()
        has_pdf = bool(obj.pdf_file)
        has_audio = bool(obj.audio_file)
        has_video = bool(obj.video_file)

        content_parts = []
        if has_main:
            content_parts.append(
                format_html('<span style="color: green;">Текст</span>')
            )
        if has_pdf:
            content_parts.append(format_html('<span style="color: blue;">PDF</span>'))
        if has_audio:
            content_parts.append(
                format_html('<span style="color: purple;">Аудио</span>')
            )
        if has_video:
            content_parts.append(format_html('<span style="color: red;">Видео</span>'))

        if not content_parts:
            return format_html('<span style="color: gray;">Нет</span>')

        return mark_safe(" | ".join(content_parts))

    has_content.short_description = "Содержимое"

    def display_image(self, obj):
        if obj.image_course_topic:
            return mark_safe(f'<img src="{obj.image_course_topic.url}" width="50" />')
        return "Нет изображения"

    display_image.short_description = "Предпросмотр"


@admin.register(TopicQuestion)
class TopicQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "training",
        "course_topic",
        "is_multiple_choice",
        "order",
        "is_actual",
        "answer_count",
    )
    list_filter = ("is_actual", "training", "course_topic", "is_multiple_choice")
    search_fields = ("title", "training__title", "course_topic__title")
    list_editable = ("order",)
    inlines = [AnswerOptionInline]
    readonly_fields = ("created_at", "updated_at")

    def answer_count(self, obj):
        count = obj.answer_options.count()
        correct = obj.answer_options.filter(is_correct=True).count()
        return format_html(
            '{} (правильных: <span style="color: green;">{}</span>)', count, correct
        )

    answer_count.short_description = "Варианты ответов"


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("order", "text_short", "topic_question", "is_correct", "is_actual")
    list_filter = ("is_actual", "is_correct", "topic_question__training")
    search_fields = ("text", "topic_question__title", "topic_question__training__title")
    readonly_fields = ("created_at", "updated_at")

    def text_short(self, obj):
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text

    text_short.short_description = "Текст ответа"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipient_name",
        "training_course",
        "course_title",
        "result",
        "completed_at",
        "expires_at",
        "created_at",
        "has_file",
    )
    list_filter = ("completed_at", "expires_at", "created_at", "training_course")
    search_fields = (
        "recipient_name",
        "course_title",
        "user__full_name",
        "user__user_name",
        "training_course__title",
    )
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")

    def has_file(self, obj):
        return bool(obj.certificate_file)

    has_file.boolean = True
    has_file.short_description = "Файл"


@admin.register(RatingTrainingCourse)
class RatingTrainingCourseAdmin(admin.ModelAdmin):
    list_display = ("student", "training_course", "rating_stars", "created_at")
    list_filter = ("rating", "training_course", "created_at")
    search_fields = (
        "student__full_name",
        "student__user_name",
        "training_course__title",
        "comment",
    )
    readonly_fields = ("created_at", "updated_at")

    def rating_stars(self, obj):
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        return format_html('<span style="color: #FFD700;">{}</span>', stars)

    rating_stars.short_description = "Оценка"


@admin.register(CourseDeadline)
class CourseDeadlineAdmin(admin.ModelAdmin):
    list_display = (
        "training_course",
        "deadline_date",
        "groups_count",
        "users_count",
        "is_past",
    )
    list_filter = ("deadline_date", "training_course")
    search_fields = ("training_course__title",)
    filter_horizontal = ("deadline_groups", "deadline_users")
    date_hierarchy = "deadline_date"
    readonly_fields = ("created_at", "updated_at")

    def groups_count(self, obj):
        return obj.deadline_groups.count()

    groups_count.short_description = "Кол-во групп"

    def users_count(self, obj):
        return obj.deadline_users.count()

    users_count.short_description = "Кол-во студентов"

    def is_past(self, obj):
        from django.utils import timezone

        return obj.deadline_date < timezone.now().date()

    is_past.boolean = True
    is_past.short_description = "Наступил"


@admin.register(NewsBlock)
class NewsBlockAdmin(admin.ModelAdmin):
    list_display = (
        "start_date_news",
        "is_important",
        "news_title",
    )
    list_filter = ("is_important", "news_title", "start_date_news")
    search_fields = ("news_title", "text_news")
    date_hierarchy = "start_date_news"
    # readonly_fields = ("created_at", "updated_at", "display_image")
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("news_title", "text_news")},
        ),
        (
            "Сроки публикации и важность",
            {"fields": ("start_date_news", "is_important")},
        ),
        # ("Изображение", {"fields": ("image", "display_image")}),
    )

    # def is_active(self, obj):
    #     from django.utils import timezone

    #     today = timezone.now().date()
    #     is_started = obj.start_date_news <= today
    #     is_not_ended = obj.end_date_news is None or obj.end_date_news >= today
    #     return is_started and is_not_ended and obj.is_published

    # is_active.boolean = True
    # is_active.short_description = "Активна"

    # def display_image(self, obj):
    #     if obj.image:
    #         return mark_safe(f'<img src="{obj.image.url}" width="50" />')
    #     return "Нет изображения"

    # display_image.short_description = "Предпросмотр"


@admin.register(UserNewsStatus)
class UserNewsStatusAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "news",
        "is_read",
        "is_pinned",
        "created_at",
    )
    list_filter = (
        "is_read",
        "is_pinned",
        "news__is_important",
        "news__start_date_news",
    )
    search_fields = (
        "user__full_name",
        "user__user_name",
        "news__news_title",
    )
    autocomplete_fields = ("user", "news")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")


@admin.register(ScormPack)
class ScormPackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "training_course",
        "course_topic",
        "name_index",
        "scorm_file",
        "is_actual",
    )
    list_filter = ("is_actual", "training_course", "course_topic")
    search_fields = (
        "training_course__title",
        "course_topic__title",
        "name_index",
    )
    list_select_related = ("training_course", "course_topic")
    readonly_fields = ("created_at", "updated_at", "manifest_data")


@admin.register(ObligatoryList)
class ObligatoryListAdmin(admin.ModelAdmin):
    list_display = ("training_course",)
    list_filter = ("training_course", "department", "jobtitle")
    search_fields = ("training_course__title", "department__name", "jobtitle__name")
    filter_horizontal = ("department", "jobtitle")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CourseAssignmentNotification)
class CourseAssignmentNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "training_course",
        "user_display",
        "notified_at",
    )
    list_filter = ("training_course", "notified_at")
    search_fields = (
        "training_course__title",
        "user__full_name",
        "user__user_name",
        "user__telegram_id",
    )
    readonly_fields = (
        "training_course",
        "user",
        "notified_at",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "notified_at"

    def user_display(self, obj):
        return obj.user.full_name or obj.user.user_name or f"ID: {obj.user.telegram_id}"

    user_display.short_description = "Пользователь"

    def has_add_permission(self, request):
        # Запрещаем ручное создание записей - они создаются только через action
        return False
