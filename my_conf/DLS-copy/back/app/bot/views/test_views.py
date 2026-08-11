from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from asgiref.sync import async_to_sync

from app.learning_app.models.courses import TrainingCourse, CourseTopic
from app.learning_app.services.test_service import TestService
from app.bot.models.telegram_user import TelegramUser
from ..serializers.test_serializers import (
    CourseTestSerializer,
    CourseTestQuestionSerializer,
    TestSubmissionSerializer,
    TestSubmissionResultSerializer,
)


class CourseTestView(APIView):
    """
    API endpoint для получения теста курса.
    Возвращает вопросы и варианты ответов для прохождения теста.
    """

    @extend_schema(
        summary="Получить тест курса",
        description="Возвращает все актуальные вопросы и варианты ответов для указанного курса",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID курса для получения теста",
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "min_test_percent_course": {"type": "integer"},
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "title": {"type": "string"},
                                "is_multiple_choice": {"type": "boolean"},
                                "order": {"type": "integer"},
                                "answer_options": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "text": {"type": "string"},
                                            "is_correct": {"type": "boolean"},
                                            "order": {"type": "integer"},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "course_id": {"type": "integer"},
                    "course_title": {"type": "string"},
                },
            },
        },
        tags=["Тестирование курсов"],
    )
    def get(self, request, course_id):
        """
        Получить тест для курса.

        Args:
            course_id (int): ID курса

        Returns:
            Response: JSON с данными теста или ошибка 404
        """
        # Получаем курс или возвращаем 404
        course = get_object_or_404(TrainingCourse, pk=course_id)

        # Проверяем, что курс не архивный
        if course.archive:
            return Response(
                {
                    "error": "Курс находится в архиве",
                    "course_id": course.id,
                    "course_title": course.title,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Проверяем наличие актуальных вопросов
        actual_questions = course.questions.filter(is_actual=True)
        if not actual_questions.exists():
            return Response(
                {
                    "error": "У данного курса нет актуальных вопросов для тестирования",
                    "course_id": course.id,
                    "course_title": course.title,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Проверяем, что у вопросов есть актуальные варианты ответов
        questions_with_answers = []
        for question in actual_questions:
            if question.answer_options.filter(is_actual=True).exists():
                questions_with_answers.append(question)

        if not questions_with_answers:
            return Response(
                {
                    "error": "У вопросов курса нет актуальных вариантов ответов",
                    "course_id": course.id,
                    "course_title": course.title,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Сериализуем и возвращаем данные
        serializer = CourseTestSerializer(course)
        data = serializer.data
        data["scope"] = "course"
        return Response(data, status=status.HTTP_200_OK)


class CourseTestSubmitView(APIView):
    """
    API endpoint для отправки результатов тестирования.
    Принимает результат теста и сохраняет его с использованием существующей логики.
    """

    @extend_schema(
        summary="Отправить результаты тестирования",
        description="Сохраняет результат теста пользователя с применением логики лучшего результата",
        request=TestSubmissionSerializer,
        responses={
            200: TestSubmissionResultSerializer,
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "details": {"type": "object"},
                },
            },
            404: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        tags=["Тестирование курсов"],
    )
    def post(self, request, course_id):
        """
        Отправить результаты тестирования.

        Args:
            course_id (int): ID курса из URL

        Returns:
            Response: JSON с результатом сохранения
        """
        # Валидируем входные данные
        serializer = TestSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Некорректные данные", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data

        # Проверяем соответствие course_id
        if validated_data.get("course_id") not in (None, course_id):
            return Response(
                {"error": "course_id в данных не соответствует курсу в URL"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if validated_data.get("topic_id"):
            return Response(
                {"error": "Для сабмита курса не передавайте topic_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверяем существование пользователя (по внутреннему id)
        try:
            user = TelegramUser.objects.get(id=validated_data["user_id"])
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

        try:
            # Используем новый метод из TestService с async_to_sync
            test_service = TestService()

            result = async_to_sync(test_service.submit_test_from_web)(
                user_id=validated_data["user_id"],
                course_id=course_id,
                topic_id=validated_data.get("topic_id"),
                quantity_correct=validated_data["quantity_correct"],
            )

            if not result.get("success"):
                return Response(
                    {
                        "error": result.get(
                            "message", "Ошибка при сохранении результатов"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Формируем ответ
            result_serializer = TestSubmissionResultSerializer(data=result)
            result_serializer.is_valid(raise_exception=True)

            return Response(result_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "error": "Ошибка при обработке результатов тестирования",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TopicTestView(APIView):
    """
    API endpoint для получения теста темы.
    """

    @extend_schema(
        summary="Получить тест темы",
        description="Возвращает все актуальные вопросы и варианты ответов для указанной темы",
        parameters=[
            OpenApiParameter(
                name="topic_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID темы для получения теста",
            )
        ],
        tags=["Тестирование тем"],
    )
    def get(self, request, topic_id: int):
        topic = get_object_or_404(CourseTopic, pk=topic_id, is_actual=True)
        actual_questions = topic.questions.filter(is_actual=True).order_by("order")
        if not actual_questions.exists():
            return Response(
                {
                    "error": "У данной темы нет актуальных вопросов для тестирования",
                    "topic_id": topic.id,
                    "topic_title": topic.title,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        questions_with_answers = [
            q for q in actual_questions if q.answer_options.filter(is_actual=True).exists()
        ]
        if not questions_with_answers:
            return Response(
                {
                    "error": "У вопросов темы нет актуальных вариантов ответов",
                    "topic_id": topic.id,
                    "topic_title": topic.title,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CourseTestSerializer(topic.training_course)
        data = serializer.data
        data["scope"] = "topic"
        data["topic_id"] = topic.id
        data["topic_title"] = topic.title
        data["questions"] = CourseTestQuestionSerializer(
            actual_questions, many=True
        ).data
        return Response(data, status=status.HTTP_200_OK)


class TopicTestSubmitView(APIView):
    """
    API endpoint для отправки результатов тестирования темы.
    """

    @extend_schema(
        summary="Отправить результаты тестирования темы",
        description="Сохраняет результат теста пользователя по теме с логикой лучшего результата",
        request=TestSubmissionSerializer,
        responses={
            200: TestSubmissionResultSerializer,
            400: {"type": "object"},
            404: {"type": "object"},
        },
        tags=["Тестирование тем"],
    )
    def post(self, request, topic_id: int):
        serializer = TestSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Некорректные данные", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = serializer.validated_data
        if data.get("topic_id") != topic_id:
            return Response(
                {"error": "topic_id в данных не соответствует теме в URL"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = TelegramUser.objects.get(id=data["user_id"])
        except TelegramUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=404)
        topic = get_object_or_404(CourseTopic, pk=topic_id, is_actual=True)
        test_service = TestService()
        try:
            result = async_to_sync(test_service.submit_test_from_web)(
                user_id=user.id,
                course_id=topic.training_course_id,
                topic_id=topic.id,
                quantity_correct=data["quantity_correct"],
            )
        except Exception as e:
            return Response(
                {"error": "Ошибка при обработке результатов теста", "details": str(e)},
                status=500,
            )
        if not result.get("success"):
            return Response(
                {"error": result.get("message", "Ошибка сохранения результата")},
                status=400,
            )
        result_serializer = TestSubmissionResultSerializer(data=result)
        result_serializer.is_valid(raise_exception=True)
        return Response(result_serializer.data, status=200)
