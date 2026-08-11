from django.shortcuts import render, get_object_or_404
from pathlib import Path
from django.http import FileResponse
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .models.additional import (
    Certificate,
    RatingTrainingCourse,
    CourseDeadline,
    NewsBlock,
    UserNewsStatus,
)
from .models.courses import (
    TagCourse,
    CourseDirection,
    TrainingCourse,
    CourseTopic,
    ScormPack,
)
from .models.testing import TopicQuestion, AnswerOption
from app.bot.models.telegram_user import TelegramUser
from app.bot.models import UserTest
from .serializer import (
    CertificateSerializer,
    RatingTrainingCourseSerializer,
    CourseDeadlineSerializer,
    NewsBlockSerializer,
    NewsBlockListSerializer,
    NewsBlockDetailSerializer,
    NewsReadRequestSerializer,
    NewsReadResponseSerializer,
    NewsPinRequestSerializer,
    NewsPinResponseSerializer,
    TagCourseSerializer,
    CourseDirectionSerializer,
    TrainingCourseSerializer,
    AvailableTrainingCourseSerializer,
    EnrollTrainingCourseResponseSerializer,
    CourseTopicSerializer,
    TopicQuestionSerializer,
    AnswerOptionSerializer,
)


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer


class RatingTrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = RatingTrainingCourse.objects.all()
    serializer_class = RatingTrainingCourseSerializer


class CourseDeadlineViewSet(viewsets.ModelViewSet):
    queryset = CourseDeadline.objects.all()
    serializer_class = CourseDeadlineSerializer


class NewsBlockViewSet(viewsets.ModelViewSet):
    queryset = NewsBlock.objects.all()
    serializer_class = NewsBlockSerializer

    @extend_schema(
        summary="Список новостей для пользователя",
        description="Возвращает список новостей с полями id, is_important, date, preview и флагом is_pinned для текущего пользователя. Закреплённые идут первыми.",
        responses={200: NewsBlockListSerializer(many=True)},
        tags=["Новости"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Детальная новость по id",
        description="Возвращает детальную новость: id, name, date, is_important, text.",
        responses={200: NewsBlockDetailSerializer},
        tags=["Новости"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        qs = NewsBlock.objects.all()
        telegram_user = getattr(
            getattr(self.request, "user", None), "telegram_user", None
        )

        if telegram_user:
            pinned_exists = UserNewsStatus.objects.filter(
                user=telegram_user,
                news=models.OuterRef("pk"),
                is_pinned=True,
            )
            read_exists = UserNewsStatus.objects.filter(
                user=telegram_user,
                news=models.OuterRef("pk"),
                is_read=True,
            )
            qs = qs.annotate(
                is_pinned=models.Exists(pinned_exists),
                is_read=models.Exists(read_exists),
            )
        else:
            qs = qs.annotate(
                is_pinned=models.Value(False, output_field=models.BooleanField()),
                is_read=models.Value(False, output_field=models.BooleanField()),
            )

        return qs.order_by("-is_pinned", "-start_date_news", "-id")

    def get_serializer_class(self):
        if self.action == "list":
            return NewsBlockListSerializer
        if self.action == "retrieve":
            return NewsBlockDetailSerializer
        return NewsBlockSerializer

    @action(detail=True, methods=["post"], url_path="read")
    @extend_schema(
        summary="Отметить новость прочитанной",
        description="Отмечает новость как прочитанную для текущего пользователя.",
        request=NewsReadRequestSerializer,
        responses={200: NewsReadResponseSerializer, 401: {"type": "object"}},
        tags=["Новости"],
    )
    def mark_read(self, request, pk=None):
        news = self.get_object()
        user = getattr(request.user, "telegram_user", None)
        if not user:
            return Response(
                {"detail": "Требуется аутентификация"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        is_read = request.data.get("is_read")
        if isinstance(is_read, str):
            is_read = is_read.lower() in ("1", "true", "yes")
        if is_read is None:
            is_read = True
        status_obj, _ = UserNewsStatus.objects.get_or_create(user=user, news=news)
        if status_obj.is_read != is_read:
            status_obj.is_read = is_read
            status_obj.save(update_fields=["is_read", "updated_at"])
        return Response(
            {"success": True, "is_read": True, "is_pinned": status_obj.is_pinned}
        )

    @action(detail=True, methods=["post"], url_path="pin")
    @extend_schema(
        summary="Закрепить/открепить новость",
        description="Устанавливает флаг закрепления новости для текущего пользователя.",
        request=NewsPinRequestSerializer,
        responses={
            200: NewsPinResponseSerializer,
            400: {"type": "object"},
            401: {"type": "object"},
        },
        tags=["Новости"],
    )
    def set_pin(self, request, pk=None):
        news = self.get_object()
        user = getattr(request.user, "telegram_user", None)
        if not user:
            return Response(
                {"detail": "Требуется аутентификация"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        is_pinned = request.data.get("is_pinned")
        if isinstance(is_pinned, str):
            is_pinned = is_pinned.lower() in ("1", "true", "yes")
        if is_pinned is None or not isinstance(is_pinned, bool):
            return Response(
                {"detail": "Передайте параметр is_pinned=true|false"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        status_obj, _ = UserNewsStatus.objects.get_or_create(user=user, news=news)
        if status_obj.is_pinned != is_pinned:
            status_obj.is_pinned = is_pinned
            status_obj.save(update_fields=["is_pinned", "updated_at"])
        return Response({"success": True, "is_pinned": status_obj.is_pinned})


class TagCourseViewSet(viewsets.ModelViewSet):
    queryset = TagCourse.objects.all()
    serializer_class = TagCourseSerializer


class CourseDirectionViewSet(viewsets.ModelViewSet):
    serializer_class = CourseDirectionSerializer

    def get_queryset(self):
        return CourseDirection.objects.prefetch_related(
            models.Prefetch(
                "trainingcourse_set",
                queryset=TrainingCourse.objects.filter(is_actual=True, archive=False),
            )
        ).filter(is_actual=True)


class TrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer

    @extend_schema(
        summary="Получить курсы пользователя",
        description="Возвращает список курсов, назначенных указанному пользователю (через прямое назначение или группы)",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID пользователя Telegram",
            )
        ],
        responses={
            200: TrainingCourseSerializer(many=True),
            404: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        tags=["Курсы пользователя"],
    )
    @action(detail=False, methods=["get"], url_path="user/(?P<user_id>[^/.]+)")
    def courses_by_user(self, request, user_id=None):
        """
        Получить список курсов пользователя.
        URL: GET /api/v1/trainingcourses/user/{user_id}/
        """
        from django.db.models import Subquery, OuterRef, Min
        from .models.additional import CourseDeadline

        try:
            user = (
                TelegramUser.objects.select_related(
                    "company", "department", "job_title"
                )
                .prefetch_related("groups")
                .get(id=user_id)
            )
        except TelegramUser.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        user_groups = user.groups.all()

        deadline_subquery = (
            CourseDeadline.objects.filter(
                training_course=OuterRef("pk"),
            )
            .filter(
                models.Q(deadline_users=user)
                | models.Q(deadline_groups__in=user_groups)
            )
            .values("deadline_date")
            .order_by("deadline_date")
        )

        courses = (
            TrainingCourse.objects.filter(
                models.Q(user=user) | models.Q(group__in=user_groups),
                archive=False,
                is_actual=True,
            )
            .distinct()
            .annotate(deadline=Subquery(deadline_subquery[:1]))
            .select_related("author", "course_direction")
            .prefetch_related("tag", "user", "group")
            .order_by("title")
        )

        serializer = self.get_serializer(
            courses,
            many=True,
            context={**self.get_serializer_context(), "user_id": user_id},
        )
        return Response(serializer.data)


class CourseTopicViewSet(viewsets.ModelViewSet):
    queryset = CourseTopic.objects.annotate(
        has_scorm=models.Exists(
            ScormPack.objects.filter(
                course_topic_id=models.OuterRef("pk"),
                is_actual=True,
            )
        )
    )
    serializer_class = CourseTopicSerializer

    @extend_schema(
        summary="Получить темы курса для пользователя",
        description="Возвращает список тем указанного курса, если курс назначен пользователю (напрямую или через группу). Темы отсортированы по порядку",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID курса",
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID пользователя Telegram",
            ),
        ],
        responses={
            200: CourseTopicSerializer(many=True),
            404: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        tags=["Список тем курса"],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="course/(?P<course_id>[^/.]+)/user/(?P<user_id>[^/.]+)",
    )
    def topics_by_course(self, request, course_id=None, user_id=None):
        """
        Получить список тем курса для пользователя.
        URL: GET /api/v1/coursetopics/course/{course_id}/user/{user_id}/
        """
        # Находим пользователя и его группы
        try:
            user = (
                TelegramUser.objects.select_related(
                    "company", "department", "job_title"
                )
                .prefetch_related("groups")
                .get(id=user_id)
            )
        except TelegramUser.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            course = TrainingCourse.objects.get(id=course_id)
        except TrainingCourse.DoesNotExist:
            return Response(
                {"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем, что курс не архивный
        if course.archive:
            return Response(
                {"error": "Курс находится в архиве"}, status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем, что курс назначен пользователю напрямую или через группу, и что он актуален
        user_groups = user.groups.all()
        has_access = (
            TrainingCourse.objects.filter(
                id=course_id,
                archive=False,
                is_actual=True,
            )
            .filter(models.Q(user=user) | models.Q(group__in=user_groups))
            .exists()
        )

        if not has_access:
            return Response(
                {"error": "Курс не назначен пользователю"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Получаем темы курса, отсортированные по порядку
        topics = (
            self.get_queryset()
            .filter(training_course=course, is_actual=True)
            .select_related("training_course")
            .order_by("order")
        )

        serializer = self.get_serializer(topics, many=True)
        return Response(serializer.data)


class ScormPackFileView(APIView):
    @extend_schema(
        summary="Получить SCORM-пакет",
        description=(
            "Возвращает ZIP-файл SCORM-пакета. "
            "Необходимо передать ровно один параметр: training_id или topic_id. "
            "Стартовый файл передаётся в заголовке X-Scorm-Name-Index."
        ),
        parameters=[
            OpenApiParameter(
                name="training_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="ID программы обучения",
            ),
            OpenApiParameter(
                name="topic_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="ID темы программы обучения",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description=(
                    "ZIP-файл. Стартовый файл находится "
                    "в заголовке X-Scorm-Name-Index."
                ),
            ),
            400: OpenApiResponse(description="Некорректные параметры запроса"),
            404: OpenApiResponse(description="SCORM-пакет не найден"),
        },
        tags=["SCORM"],
    )
    def get(self, request):
        training_id = request.query_params.get("training_id")
        topic_id = request.query_params.get("topic_id")

        # Должен быть передан ровно один параметр.
        if (training_id is None) == (topic_id is None):
            return Response(
                {
                    "detail": (
                        "Передайте ровно один параметр: "
                        "training_id или topic_id."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_id = training_id if training_id is not None else topic_id

        try:
            object_id = int(raw_id)
            if object_id <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {"detail": "ID должен быть положительным целым числом."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        scorm_packs = ScormPack.objects.filter(is_actual=True)

        if training_id is not None:
            scorm_packs = scorm_packs.filter(
                training_course_id=object_id,
                course_topic__isnull=True,
            )
        else:
            scorm_packs = scorm_packs.filter(
                course_topic_id=object_id,
            )

        scorm_pack = scorm_packs.order_by("-updated_at", "-id").first()

        if scorm_pack is None:
            return Response(
                {"detail": "SCORM-пакет не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            scorm_file = scorm_pack.scorm_file.open("rb")
        except (FileNotFoundError, OSError):
            return Response(
                {"detail": "Файл SCORM-пакета не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response = FileResponse(
            scorm_file,
            as_attachment=True,
            filename=Path(scorm_pack.scorm_file.name).name,
            content_type="application/zip",
        )
        response["X-Scorm-Name-Index"] = scorm_pack.name_index or ""

        return response



class TopicQuestionViewSet(viewsets.ModelViewSet):
    queryset = TopicQuestion.objects.all()
    serializer_class = TopicQuestionSerializer


class AnswerOptionViewSet(viewsets.ModelViewSet):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer


class AvailableTrainingCourseView(APIView):
    """
    Отдельный endpoint для списка открытых курсов (самозапись).
    Не затрагивает текущие CourseDirection/TrainingCourse вью.
    """

    @extend_schema(
        summary="Список открытых курсов для самозаписи",
        description=(
            "Возвращает курсы с флагом open_course=True, is_actual=True, archive=False. "
            "Исключает курсы, где пользователь уже назначен напрямую или через группы."
        ),
        responses={
            200: AvailableTrainingCourseSerializer(many=True),
            401: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        tags=["Курсы для самозаписи"],
    )
    def get(self, request):
        # Проверяем аутентификацию и наличие telegram_user у CustomUser
        telegram_user = getattr(getattr(request, "user", None), "telegram_user", None)
        if not telegram_user:
            return Response(
                {"detail": "Требуется аутентификация"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Группы пользователя для исключения уже назначенных курсов
        user_groups = telegram_user.groups.all()

        # Курсы, куда пользователь уже назначен (прямо или через группы)
        assigned_course_ids = set(
            TrainingCourse.objects.filter(
                models.Q(user=telegram_user) | models.Q(group__in=user_groups)
            ).values_list("id", flat=True)
        )

        # Открытые курсы, доступные для записи
        courses = (
            TrainingCourse.objects.filter(
                is_actual=True,
                archive=False,
                open_course=True,
            )
            .exclude(id__in=assigned_course_ids)
            .select_related("course_direction", "author")
            .prefetch_related("tag")
            .order_by("title")
        )

        serializer = AvailableTrainingCourseSerializer(
            courses,
            many=True,
            context={
                "request": request,
                "user_id": telegram_user.id,
                "assigned_course_ids": assigned_course_ids,
            },
        )
        return Response(serializer.data)


class EnrollTrainingCourseView(APIView):
    """
    Отдельный endpoint для самозаписи на открытый курс.
    Не трогаем существующие вьюсетами маршруты.
    """

    @extend_schema(
        summary="Записаться на открытый курс",
        description=(
            "Самозапись пользователя на курс. Допустимы только курсы "
            "is_actual=True, archive=False, open_course=True. "
            "Если пользователь уже назначен напрямую или через группу, вернёт already_enrolled."
        ),
        responses={
            200: EnrollTrainingCourseResponseSerializer,
            401: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        tags=["Курсы для самозаписи"],
    )
    def post(self, request, course_id: int):
        # Проверяем аутентификацию и наличие telegram_user
        telegram_user = getattr(getattr(request, "user", None), "telegram_user", None)
        if not telegram_user:
            return Response(
                {"detail": "Требуется аутентификация"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Проверяем доступность курса
        try:
            course = (
                TrainingCourse.objects.select_related("course_direction", "author")
                .prefetch_related("tag", "user", "group")
                .get(
                    pk=course_id,
                    is_actual=True,
                    archive=False,
                    open_course=True,
                )
            )
        except TrainingCourse.DoesNotExist:
            return Response(
                {"detail": "Курс недоступен для самозаписи"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_groups = telegram_user.groups.all()
        is_already_enrolled = (
            TrainingCourse.objects.filter(pk=course.pk)
            .filter(models.Q(user=telegram_user) | models.Q(group__in=user_groups))
            .exists()
        )

        context = {
            "user_id": telegram_user.id,
            "assigned_course_ids": {course.id},
        }

        # Если уже записан — возвращаем флаг
        if is_already_enrolled:
            serializer = AvailableTrainingCourseSerializer(course, context=context)
            return Response(
                {
                    "detail": "Пользователь уже записан на курс",
                    "already_enrolled": True,
                    "enrolled": False,
                    "course": serializer.data,
                }
            )

        # Добавляем пользователя в курс
        course.user.add(telegram_user)
        serializer = AvailableTrainingCourseSerializer(course, context=context)
        return Response(
            {
                "detail": "Запись на курс выполнена",
                "enrolled": True,
                "already_enrolled": False,
                "course": serializer.data,
            }
        )


def topic_text_webapp_view(request, topic_pk):
    topic = get_object_or_404(CourseTopic, pk=topic_pk)
    context = {
        "topic_title": topic.title,
        "topic_main_text": topic.main_text,
        "topic_image_url": (
            topic.image_course_topic.url
            if topic.image_course_topic and hasattr(topic.image_course_topic, "url")
            else None
        ),
    }
    return render(request, "webapp/topic_text_display.html", context)


def bot_info_webapp_view(request):
    """
    WebApp-страница "О боте".
    Берет HTML-текст и изображение из SettingsBot (берется первая запись, если компания не указана).
    """
    # Для простоты берем первые доступные настройки
    settings_obj = None
    # В AsyncRepository методы async, но внутри мы можем синхронно обратиться к ORM для простоты вьюхи.
    # Поэтому здесь напрямую используем модель, чтобы не создавать event loop в Django-вьюхе.
    from app.organization.models import SettingsBot as SettingsBotModel

    settings_obj = SettingsBotModel.objects.select_related("company").first()

    from datetime import datetime

    context = {
        "company_name": (
            settings_obj.company.name if settings_obj and settings_obj.company else ""
        ),
        "bot_help_html": (
            settings_obj.bot_help_text
            if settings_obj and settings_obj.bot_help_text
            else ""
        ),
        "bot_version": (
            settings_obj.bot_version
            if settings_obj and settings_obj.bot_version
            else ""
        ),
        "image_help_url": (
            settings_obj.image_help.url
            if settings_obj and settings_obj.image_help
            else None
        ),
        "current_year": datetime.now().year,
    }
    return render(request, "webapp/bot_info.html", context)


def progress_webapp_view(request):
    """
    WebApp-страница прогресса пользователя по тестам.
    Требует user_id в query (?user_id=ID). Собирает список тестов и суммарную статистику.
    """
    user_id = request.GET.get("user_id")
    if not user_id:
        return render(
            request,
            "webapp/progress.html",
            {"error_message": "ID пользователя не найден"},
        )

    try:
        telegram_user = TelegramUser.objects.select_related("company").get(
            telegram_id=user_id
        )
    except TelegramUser.DoesNotExist:
        return render(
            request, "webapp/progress.html", {"error_message": "Пользователь не найден"}
        )

    # Все тесты пользователя
    user_tests = (
        UserTest.objects.filter(user=telegram_user)
        .select_related("training")
        .order_by("training__title")
    )

    if not user_tests.exists():
        return render(
            request,
            "webapp/progress.html",
            {
                "user": telegram_user,
                "no_tests_message": "Пользователь еще не выполнял тесты.",
            },
        )

    tests = []
    successful_tests = 0
    total_tests = user_tests.count()

    for result_test in user_tests:
        course_name = (
            result_test.training.title if result_test.training else "Без названия"
        )
        result = result_test.quantity_correct
        passed = "Да" if result_test.complete else "Нет"
        passed_class = "success" if result_test.complete else "fail"

        tests.append(
            {
                "course_name": course_name,
                "result": result,
                "passed": passed,
                "passed_class": passed_class,
            }
        )

        if result_test.complete:
            successful_tests += 1

    all_tests_passed = successful_tests == total_tests and total_tests > 0

    # Картинка прогресса из SettingsBot
    from app.organization.models import SettingsBot as SettingsBotModel

    settings_obj = SettingsBotModel.objects.select_related("company").first()
    if all_tests_passed:
        progress_image_url = (
            settings_obj.image_progress_good.url
            if settings_obj and settings_obj.image_progress_good
            else None
        )
    else:
        progress_image_url = (
            settings_obj.image_progress_bad.url
            if settings_obj and settings_obj.image_progress_bad
            else None
        )

    return render(
        request,
        "webapp/progress.html",
        {
            "user": telegram_user,
            "tests": tests,
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "all_tests_passed": all_tests_passed,
            "progress_image_url": progress_image_url,
        },
    )


"""Вью по статистике обучения"""

from collections import defaultdict
from typing import Dict, Set, Tuple
from datetime import datetime, timedelta
from django.utils import timezone

from django.contrib import admin
from django.db.models import Count, Avg, Q, F, Max
from django.template.response import TemplateResponse
from django.urls import reverse

from app.learning_app.models import (
    TrainingCourse,
    CourseTopic,
    RatingTrainingCourse,
    CourseDeadline,
)
from app.bot.models import TelegramUser, UserRead, UserTest


def statistics_education_view(request):
    """
    Админ-страница: Статистика обучения
    Вкладки:
    1. courses - Курсы (общая статистика)
    2. students - Студенты (общая статистика)
    3. ratings - Рейтинги курсов
    4. deadlines - Дедлайны и их выполнение
    5. topics - Прогресс по темам
    6. tests - Результаты тестирования
    7. top_students - Топ студентов
    """
    active_tab = request.GET.get("tab", "courses")

    # Какие курсы показываем (обычно только не архивные)
    courses = list(TrainingCourse.objects.filter(archive=False).only("id", "title"))
    course_ids = [c.id for c in courses]

    # --- 1) Пользователи, назначенные НАПРЯМУЮ на курсы
    direct_users_map: Dict[int, Set[int]] = defaultdict(set)  # course_id -> {user_id}
    for cid, uid in TrainingCourse.objects.filter(id__in=course_ids).values_list(
        "id", "user__id"
    ):
        if uid:
            direct_users_map[cid].add(uid)

    # --- 2) Группы, привязанные к курсам (course_id -> {group_id})
    course_groups_map: Dict[int, Set[int]] = defaultdict(set)
    for cid, gid in TrainingCourse.objects.filter(id__in=course_ids).values_list(
        "id", "group__id"
    ):
        if gid:
            course_groups_map[cid].add(gid)

    # Все уникальные group_id по всем курсам
    all_group_ids: Set[int] = set()
    for gids in course_groups_map.values():
        all_group_ids.update(gids)

    # --- 3) Пользователи в группах (group_id -> {user_id})
    group_users_map: Dict[int, Set[int]] = defaultdict(set)
    if all_group_ids:
        for uid, gid in TelegramUser.objects.filter(
            groups__id__in=all_group_ids
        ).values_list("id", "groups__id"):
            if uid and gid:
                group_users_map[gid].add(uid)

    # --- 4) Темы по курсам: сколько тем в каждом курсе (для проверки “все прочитано”)
    topics_count: Dict[int, int] = defaultdict(int)  # course_id -> count
    for row in (
        CourseTopic.objects.filter(training_course_id__in=course_ids)
        .values("training_course_id")
        .annotate(cnt=Count("id"))
    ):
        topics_count[row["training_course_id"]] = row["cnt"]

    # --- 5) Прочтения: (user_id, course_id) -> количество уникальных прочитанных тем
    reads_map: Dict[Tuple[int, int], int] = defaultdict(int)
    for row in (
        UserRead.objects.filter(course_id__in=course_ids, is_read=True)
        .values("user_id", "course_id")
        .annotate(cnt=Count("topic_id", distinct=True))
    ):
        reads_map[(row["user_id"], row["course_id"])] = row["cnt"]

    # --- 6) Сданные тесты: множество пар (user_id, course_id)
    tests_passed_pairs: Set[Tuple[int, int]] = set(
        UserTest.objects.filter(training_id__in=course_ids, complete=True).values_list(
            "user_id", "training_id"
        )
    )

    # --- 7) Назначенные пользователи по каждому курсу (объединяем прямых и из групп)
    assigned_users_map: Dict[int, Set[int]] = defaultdict(set)
    for c in courses:
        users = set(direct_users_map[c.id])
        for gid in course_groups_map[c.id]:
            users |= group_users_map.get(gid, set())
        assigned_users_map[c.id] = users

    # --- 8) Таблица «Курсы»
    courses_rows = []
    all_user_ids: Set[int] = set()
    for c in courses:
        users = assigned_users_map[c.id]
        all_user_ids |= users

        total_students = len(users)
        total_topics = topics_count.get(c.id, 0)

        completed = 0
        if total_students:
            for uid in users:
                all_read = reads_map.get((uid, c.id), 0) >= total_topics
                test_ok = (uid, c.id) in tests_passed_pairs
                if all_read and test_ok:
                    completed += 1

        not_completed = total_students - completed

        courses_rows.append(
            {
                "id": c.id,
                "title": c.title,
                "students_count": total_students,
                "completed": completed,
                "not_completed": not_completed,
                "admin_change_url": reverse(
                    "admin:learning_app_trainingcourse_change", args=[c.id]
                ),
            }
        )

    # --- 9) Таблица «Студенты»
    # Для начала: какие курсы назначены конкретному пользователю
    user_courses_map: Dict[int, Set[int]] = defaultdict(set)  # user_id -> {course_ids}
    for cid, users in assigned_users_map.items():
        for uid in users:
            user_courses_map[uid].add(cid)

    # Имена пользователей (пытаемся взять fullname, иначе собираем ФИО, иначе username/ID)
    users_info_qs = TelegramUser.objects.filter(id__in=all_user_ids).values(
        "id", "full_name", "first_name", "last_name", "middle_name", "user_name"
    )

    def _name(u):
        return (
            u.get("full_name")
            or " ".join(
                x
                for x in [u.get("last_name"), u.get("first_name"), u.get("middle_name")]
                if x
            )
            or u.get("user_name")
            or f"#{u['id']}"
        )

    users_info = {u["id"]: _name(u) for u in users_info_qs}

    students_rows = []
    for uid, course_set in user_courses_map.items():
        total = len(course_set)
        completed = 0
        for cid in course_set:
            total_topics = topics_count.get(cid, 0)
            all_read = reads_map.get((uid, cid), 0) >= total_topics
            test_ok = (uid, cid) in tests_passed_pairs
            if all_read and test_ok:
                completed += 1
        not_completed = total - completed

        students_rows.append(
            {
                "user_id": uid,
                "full_name": users_info.get(uid, f"#{uid}"),
                "courses_total": total,
                "courses_completed": completed,
                "courses_not_completed": not_completed,
                # При желании: ссылка на пользователя в админке (если есть ModelAdmin)
                # "admin_user_url": reverse("admin:bot_telegramuser_change", args=[uid]),
            }
        )

    # Сортировки (по убыванию интересных метрик)
    courses_rows.sort(key=lambda r: (r["completed"], r["students_count"]), reverse=True)
    students_rows.sort(
        key=lambda r: (r["courses_completed"], r["courses_total"]), reverse=True
    )

    # === ВКЛАДКА 3: РЕЙТИНГИ КУРСОВ ===
    ratings_rows = []
    if active_tab == "ratings":
        for c in courses:
            ratings_qs = RatingTrainingCourse.objects.filter(training_course=c)
            ratings_count = ratings_qs.count()

            if ratings_count > 0:
                avg_rating = ratings_qs.aggregate(Avg("rating"))["rating__avg"]
                positive_count = ratings_qs.filter(rating__gte=4).count()
                positive_percent = round((positive_count / ratings_count) * 100, 1)

                # Последние комментарии
                recent_comments = list(
                    ratings_qs.filter(comment__isnull=False)
                    .exclude(comment="")
                    .order_by("-created_at")[:3]
                    .values(
                        "student__full_name", "student__user_name", "rating", "comment"
                    )
                )

                for comment in recent_comments:
                    comment["student_name"] = (
                        comment["student__full_name"]
                        or comment["student__user_name"]
                        or "Аноним"
                    )

                ratings_rows.append(
                    {
                        "course_id": c.id,
                        "course_title": c.title,
                        "avg_rating": round(avg_rating, 2) if avg_rating else 0,
                        "stars": "⭐" * int(round(avg_rating)) if avg_rating else "",
                        "ratings_count": ratings_count,
                        "positive_percent": positive_percent,
                        "recent_comments": recent_comments,
                        "admin_change_url": reverse(
                            "admin:learning_app_trainingcourse_change", args=[c.id]
                        ),
                    }
                )

        ratings_rows.sort(
            key=lambda r: (r["avg_rating"], r["ratings_count"]), reverse=True
        )

    # === ВКЛАДКА 4: ДЕДЛАЙНЫ ===
    deadlines_rows = []
    if active_tab == "deadlines":
        deadlines_qs = CourseDeadline.objects.filter(
            training_course_id__in=course_ids
        ).select_related("training_course")

        for deadline in deadlines_qs:
            course_id = deadline.training_course.id

            # Получаем пользователей с этим дедлайном
            deadline_user_ids = set(
                deadline.deadline_users.values_list("id", flat=True)
            )
            for gid in deadline.deadline_groups.values_list("id", flat=True):
                deadline_user_ids |= group_users_map.get(gid, set())

            total_with_deadline = len(deadline_user_ids)

            if total_with_deadline == 0:
                continue

            # Проверяем статус выполнения
            completed_before = 0
            completed_after = 0
            not_completed = 0

            for uid in deadline_user_ids:
                total_topics = topics_count.get(course_id, 0)
                all_read = reads_map.get((uid, course_id), 0) >= total_topics
                test_ok = (uid, course_id) in tests_passed_pairs

                if all_read and test_ok:
                    # Проверяем дату завершения (берем дату последнего теста)
                    last_test = (
                        UserTest.objects.filter(
                            user_id=uid, training_id=course_id, complete=True
                        )
                        .order_by("-created_at")
                        .first()
                    )

                    if last_test and last_test.created_at:
                        completion_date = last_test.created_at.date()
                        if completion_date <= deadline.deadline_date:
                            completed_before += 1
                        else:
                            completed_after += 1
                else:
                    not_completed += 1

            # Вычисляем оставшееся время
            today = timezone.now().date()
            days_left = (deadline.deadline_date - today).days

            if days_left < 0:
                status = "Просрочен"
                status_class = "danger"
            elif days_left == 0:
                status = "Сегодня"
                status_class = "warning"
            elif days_left <= 7:
                status = f"Осталось {days_left} дн."
                status_class = "warning"
            else:
                status = f"Осталось {days_left} дн."
                status_class = "success"

            deadlines_rows.append(
                {
                    "course_title": deadline.training_course.title,
                    "deadline_date": deadline.deadline_date,
                    "total_students": total_with_deadline,
                    "completed_before": completed_before,
                    "completed_after": completed_after,
                    "not_completed": not_completed,
                    "days_left": days_left,
                    "status": status,
                    "status_class": status_class,
                }
            )

        deadlines_rows.sort(key=lambda r: r["deadline_date"])

    # === ВКЛАДКА 5: ПРОГРЕСС ПО ТЕМАМ ===
    topics_rows = []
    if active_tab == "topics":
        topics_qs = CourseTopic.objects.filter(
            training_course_id__in=course_ids
        ).select_related("training_course")

        for topic in topics_qs:
            course_id = topic.training_course.id
            assigned_users = assigned_users_map.get(course_id, set())
            total_assigned = len(assigned_users)

            if total_assigned == 0:
                continue

            # Сколько прочитали эту тему
            read_count = UserRead.objects.filter(
                course_id=course_id, topic=topic, is_read=True
            ).count()

            read_percent = (
                round((read_count / total_assigned) * 100, 1)
                if total_assigned > 0
                else 0
            )
            not_read_count = total_assigned - read_count

            # Последняя дата прочтения (если есть прочтения)
            last_read_date = UserRead.objects.filter(
                course_id=course_id, topic=topic, is_read=True
            ).aggregate(Max("read_at"))["read_at__max"]

            topics_rows.append(
                {
                    "course_title": topic.training_course.title,
                    "topic_title": topic.title,
                    "topic_order": topic.order,
                    "total_assigned": total_assigned,
                    "read_count": read_count,
                    "read_percent": read_percent,
                    "not_read_count": not_read_count,
                    "last_read_date": (
                        last_read_date.strftime("%d.%m.%Y %H:%M")
                        if last_read_date
                        else "—"
                    ),
                }
            )

        # Сортируем: сначала самые непрочитанные
        topics_rows.sort(key=lambda r: r["read_percent"])

    # === ВКЛАДКА 6: РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ===
    tests_rows = []
    if active_tab == "tests":
        for c in courses:
            all_tests = UserTest.objects.filter(training_id=c.id)
            total_attempts = all_tests.count()

            if total_attempts == 0:
                continue

            successful_tests = all_tests.filter(complete=True)
            successful_count = successful_tests.count()

            # Первая попытка успешна
            unique_users = all_tests.values("user_id").distinct()
            first_attempt_success = 0

            for user_data in unique_users:
                uid = user_data["user_id"]
                first_test = (
                    all_tests.filter(user_id=uid).order_by("created_at").first()
                )
                if first_test and first_test.complete:
                    first_attempt_success += 1

            # Средний процент правильных ответов
            avg_correct = successful_tests.aggregate(Avg("quantity_correct"))[
                "quantity_correct__avg"
            ]

            # Среднее количество попыток
            retake_count = 0
            for user_data in unique_users:
                uid = user_data["user_id"]
                user_attempts = all_tests.filter(user_id=uid).count()
                if user_attempts > 1:
                    retake_count += user_attempts - 1

            avg_attempts = (
                round(total_attempts / unique_users.count(), 1)
                if unique_users.count() > 0
                else 0
            )

            tests_rows.append(
                {
                    "course_title": c.title,
                    "total_attempts": total_attempts,
                    "successful_count": successful_count,
                    "first_attempt_success": first_attempt_success,
                    "first_attempt_percent": (
                        round((first_attempt_success / unique_users.count()) * 100, 1)
                        if unique_users.count() > 0
                        else 0
                    ),
                    "avg_correct": round(avg_correct, 1) if avg_correct else 0,
                    "retake_count": retake_count,
                    "avg_attempts": avg_attempts,
                    "admin_change_url": reverse(
                        "admin:learning_app_trainingcourse_change", args=[c.id]
                    ),
                }
            )

        tests_rows.sort(key=lambda r: r["successful_count"], reverse=True)

    # === ВКЛАДКА 7: ТОП СТУДЕНТОВ (расширенная) ===
    top_students_rows = []
    if active_tab == "top_students":
        # Собираем все тесты пользователей
        user_tests_data = defaultdict(list)
        for test in UserTest.objects.filter(training_id__in=course_ids).values(
            "user_id", "quantity_correct", "training_id", "complete", "created_at"
        ):
            user_tests_data[test["user_id"]].append(test)

        for uid, course_set in user_courses_map.items():
            total = len(course_set)
            completed = 0
            total_score = 0
            test_count = 0
            attempts_count = 0
            last_activity = None

            for cid in course_set:
                total_topics = topics_count.get(cid, 0)
                all_read = reads_map.get((uid, cid), 0) >= total_topics
                test_ok = (uid, cid) in tests_passed_pairs
                if all_read and test_ok:
                    completed += 1

            # Средний балл по тестам
            user_tests = user_tests_data.get(uid, [])
            if user_tests:
                for test in user_tests:
                    if test["complete"] and test["quantity_correct"]:
                        total_score += test["quantity_correct"]
                        test_count += 1
                    attempts_count += 1

                    if test["created_at"]:
                        if last_activity is None or test["created_at"] > last_activity:
                            last_activity = test["created_at"]

            avg_score = round(total_score / test_count, 1) if test_count > 0 else 0
            avg_attempts = (
                round(attempts_count / len(course_set), 1) if len(course_set) > 0 else 0
            )

            not_completed = total - completed

            top_students_rows.append(
                {
                    "user_id": uid,
                    "full_name": users_info.get(uid, f"#{uid}"),
                    "courses_total": total,
                    "courses_completed": completed,
                    "courses_not_completed": not_completed,
                    "avg_score": avg_score,
                    "avg_attempts": avg_attempts,
                    "last_activity": (
                        last_activity.strftime("%d.%m.%Y") if last_activity else "—"
                    ),
                }
            )

        # Сортируем по завершенным курсам и среднему баллу
        top_students_rows.sort(
            key=lambda r: (r["courses_completed"], r["avg_score"]), reverse=True
        )

    context = dict(
        admin.site.each_context(request),
        title="Статистика обучения",
        active_tab=active_tab,
        courses_rows=courses_rows,
        students_rows=students_rows,
        ratings_rows=ratings_rows,
        deadlines_rows=deadlines_rows,
        topics_rows=topics_rows,
        tests_rows=tests_rows,
        top_students_rows=top_students_rows,
    )
    return TemplateResponse(request, "admin/statistics_education.html", context)
