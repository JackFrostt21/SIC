from collections import defaultdict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from ..models import UserTest, TelegramUser
from ..serializers.testlist_serializers import UserTestListSerializer

class UserTestListView(APIView):
    """
    API endpoint для получения списка результатов тестирования пользователя.
    """

    @extend_schema(
        summary="Получить список тестов пользователя",
        description="Возвращает для пользователя список тестов с информацией о курсе, количестве правильных ответов и флаге complete.",
        parameters=[
            OpenApiParameter(
                name="telegram_user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID пользователя Telegram",
            )
        ],
        responses={
            200: UserTestListSerializer,
            404: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "telegram_user_id": {"type": "integer"},
                },
            },
        },
        tags=["Список тестов"],
    )
    def get(self, request, telegram_user_id):
        # 1) Проверяем, что пользователь существует
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

        # 2) Получаем все записи UserTest для этого пользователя
        user_tests = UserTest.objects.filter(user=user).select_related('training')

        # 3) Если записей нет — отдаем пустой список
        if not user_tests.exists():
            response_data = {
                "telegram_user_id": user.id,
                "full_name": user.full_name or user.user_name or "Пользователь",
                "tests": [],
            }
            serializer = UserTestListSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 4) Собираем список словарей для сериализатора
        tests_list = []
        for ut in user_tests:
            tests_list.append({
                "training_id": ut.training.id,
                "training_title": ut.training.title,
                "quantity_correct": ut.quantity_correct or 0,
                "complete": ut.complete,
            })

        # 5) Формируем окончательный словарь ответа
        response_data = {
            "telegram_user_id": user.id,
            "full_name": user.full_name or user.user_name or "Пользователь",
            "tests": tests_list,
        }
        serializer = UserTestListSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)