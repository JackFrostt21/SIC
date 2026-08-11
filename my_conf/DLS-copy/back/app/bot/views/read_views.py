from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from collections import defaultdict

from app.bot.models.education_data import UserRead
from app.bot.models.telegram_user import TelegramUser
from app.learning_app.models.courses import TrainingCourse, CourseTopic
from ..serializers.read_serializers import (
    CourseReadListSerializer,
    MarkTopicReadSerializer,
    MarkTopicReadResultSerializer,
    UnfinishedCoursesListSerializer,
)


class CourseReadView(APIView):
    """
    API endpoint для получения списка курсов пользователя с отметками прочтения.
    Возвращает только курсы, для которых есть записи в таблице UserRead.
    """

    @extend_schema(
        summary="Получить список курсов с отметками прочтения",
        description="Возвращает список курсов пользователя с темами и информацией о прочтении. Показывает только курсы, для которых есть записи в UserRead.",
        parameters=[
            OpenApiParameter(
                name="telegram_user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID пользователя Telegram для получения списка курсов",
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "telegram_user_id": {"type": "integer"},
                    "full_name": {"type": "string"},
                    "courses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "title": {"type": "string"},
                                "topics": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "title": {"type": "string"},
                                            "order": {"type": "integer"},
                                            "is_read": {"type": "boolean"},
                                            "read_at": {
                                                "type": "string",
                                                "format": "date-time",
                                                "nullable": True,
                                            },
                                        },
                                    },
                                },
                                "total_topics": {"type": "integer"},
                                "read_topics": {"type": "integer"},
                                "progress_percent": {"type": "integer"},
                            },
                        },
                    },
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "telegram_user_id": {"type": "integer"},
                },
            },
        },
        tags=["Чтение материалов"],
    )
    def get(self, request, telegram_user_id):
        """
        Получить список курсов с отметками прочтения.

        Args:
            telegram_user_id (int): ID пользователя Telegram из URL

        Returns:
            Response: JSON со списком курсов и информацией о прочтении
        """
        # Проверяем существование пользователя
        try:
            user = TelegramUser.objects.get(id=telegram_user_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {
                    "error": "Пользователь не найден",
                    "telegram_user_id": telegram_user_id,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Получаем все записи UserRead для данного пользователя
        user_reads = (
            UserRead.objects.filter(user=user, is_actual=True)
            .select_related("course", "topic")
            .order_by("course_id", "topic__order")
        )

        if not user_reads.exists():
            # Если нет записей UserRead, возвращаем пустой список курсов
            response_data = {
                "telegram_user_id": user.id,
                "full_name": user.full_name or user.user_name or "Пользователь",
                "courses": [],
            }
            serializer = CourseReadListSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Группируем данные по курсам
        courses_dict = defaultdict(lambda: {"course": None, "topics": []})

        for user_read in user_reads:
            course_id = user_read.course.id

            # Сохраняем информацию о курсе
            if courses_dict[course_id]["course"] is None:
                courses_dict[course_id]["course"] = user_read.course

            # Добавляем информацию о теме
            topic_data = {
                "id": user_read.topic.id,
                "title": user_read.topic.title,
                "order": getattr(user_read.topic, "order", 0),
                "is_read": user_read.is_read,
                "read_at": user_read.read_at,
            }
            courses_dict[course_id]["topics"].append(topic_data)

        # Формируем итоговый список курсов
        courses_list = []
        for course_id, course_data in courses_dict.items():
            course = course_data["course"]
            topics = course_data["topics"]

            # Вычисляем статистику
            total_topics = len(topics)
            read_topics = sum(1 for topic in topics if topic["is_read"])
            progress_percent = (
                round((read_topics / total_topics) * 100) if total_topics > 0 else 0
            )

            # Сортируем темы по order
            topics_sorted = sorted(topics, key=lambda x: x["order"])

            course_info = {
                "id": course.id,
                "title": course.title,
                "topics": topics_sorted,
                "total_topics": total_topics,
                "read_topics": read_topics,
                "progress_percent": progress_percent,
            }
            courses_list.append(course_info)

        # Сортируем курсы по ID
        courses_list.sort(key=lambda x: x["id"])

        # Формируем ответ
        response_data = {
            "telegram_user_id": user.id,
            "full_name": user.full_name or user.user_name or "Пользователь",
            "courses": courses_list,
        }

        serializer = CourseReadListSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseReadSubmitView(APIView):
    """
    API endpoint для отметки темы как прочитанной.
    Обновляет или создает запись в таблице UserRead.
    """

    @extend_schema(
        summary="Отметить тему как прочитанную",
        description="Обновляет статус прочтения темы для пользователя. Создает новую запись UserRead или обновляет существующую.",
        parameters=[
            OpenApiParameter(
                name="telegram_user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID пользователя Telegram",
            ),
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID курса",
            ),
            OpenApiParameter(
                name="topic_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID темы для отметки",
            ),
        ],
        request=MarkTopicReadSerializer,
        responses={
            200: MarkTopicReadResultSerializer,
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "details": {"type": "object"},
                },
            },
            404: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        tags=["Чтение материалов"],
    )
    def post(self, request, telegram_user_id, course_id, topic_id):
        """
        Отметить тему как прочитанную.

        Args:
            telegram_user_id (int): ID пользователя Telegram из URL
            course_id (int): ID курса из URL
            topic_id (int): ID темы из URL

        Returns:
            Response: JSON с результатом обновления
        """
        # Валидируем входные данные
        serializer = MarkTopicReadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Некорректные данные", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data

        # Проверяем существование пользователя
        try:
            user = TelegramUser.objects.get(id=telegram_user_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем существование курса
        try:
            course = TrainingCourse.objects.get(pk=course_id)
        except TrainingCourse.DoesNotExist:
            return Response(
                {"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем, что курс не архивный
        if course.archive:
            return Response(
                {"error": "Курс находится в архиве"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем существование темы и её принадлежность к курсу
        try:
            topic = CourseTopic.objects.get(pk=topic_id, training_course=course)
        except CourseTopic.DoesNotExist:
            return Response(
                {"error": "Тема не найдена или не принадлежит указанному курсу"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Обновляем или создаем запись UserRead
            user_read, created = UserRead.objects.update_or_create(
                user=user,
                course=course,
                topic=topic,
                defaults={
                    "is_read": validated_data["is_read"],
                    "is_actual": True,
                },
            )

            # Формируем ответ
            action = (
                "отмечена как прочитанная"
                if validated_data["is_read"]
                else "отмечена как непрочитанная"
            )
            result_data = {
                "success": True,
                "message": f'Тема "{topic.title}" {action}',
                "topic_title": topic.title,
                "read_at": user_read.read_at if user_read.is_read else None,
            }

            result_serializer = MarkTopicReadResultSerializer(data=result_data)
            result_serializer.is_valid(raise_exception=True)

            return Response(result_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "error": "Ошибка при обновлении статуса прочтения",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UnfinishedCoursesView(APIView):
    """
    API endpoint для получения списка непройденных курсов пользователя.
    Использует ту же логику, что и рассылка напоминаний в Telegram.
    """

    @extend_schema(
        summary="Получить список непройденных курсов",
        description='Возвращает список курсов, назначенных пользователю напрямую или через группы, где тест не пройден (test_status != "completed_passed"). Курсы с истекшим дедлайном исключаются.',
        parameters=[
            OpenApiParameter(
                name="telegram_user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID пользователя Telegram для получения списка непройденных курсов",
            )
        ],
        responses={
            200: UnfinishedCoursesListSerializer,
            404: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "telegram_user_id": {"type": "integer"},
                },
            },
        },
        tags=["Не пройденные курсы"],
    )
    def get(self, request, telegram_user_id):
        """
        Получить список непройденных курсов для пользователя.

        Args:
            telegram_user_id (int): ID записи TelegramUser (pk) из URL

        Returns:
            Response: JSON со списком непройденных курсов
        """
        import asyncio
        from app.learning_app.repositories.course_repository import CourseRepository

        # Проверяем существование пользователя по id модели
        try:
            user = TelegramUser.objects.get(id=telegram_user_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {
                    "error": "Пользователь не найден",
                    "telegram_user_id": telegram_user_id,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Получаем доступные курсы через репозиторий (передаём telegram_id из модели)
        course_repo = CourseRepository()
        try:
            courses = asyncio.run(course_repo.get_available_courses(user.telegram_id))
        except Exception as e:
            return Response(
                {
                    "error": "Ошибка при получении списка курсов",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Фильтруем только непройденные курсы (та же логика что в рассылке)
        unfinished = [c for c in courses if c.get("test_status") != "completed_passed"]

        # Формируем список курсов для ответа
        courses_list = []
        for item in unfinished:
            course = item["course"]
            courses_list.append(
                {
                    "id": course.id,
                    "title": course.title,
                    "test_status": item.get("test_status"),
                }
            )

        # Формируем ответ
        response_data = {
            "telegram_user_id": user.id,
            "full_name": user.full_name or user.user_name or "Пользователь",
            "courses": courses_list,
        }

        serializer = UnfinishedCoursesListSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
