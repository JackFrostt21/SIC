from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from django.db.models import F

from app.bot.models.rating import UserRating
from app.bot.models.telegram_user import TelegramUser
from app.bot.serializers.rating_serializers import LeaderboardUserSerializer


class UserRatingViewSet(viewsets.ViewSet):
    """
    Рейтинг пользователей (денормализованные очки из UserRating):
    - GET /api/v1/user-rating/ — полный рейтинг (3 блока)
    """

    def _get_place_for_points(self, points: int) -> int:
        # dense-rank: место = 1 + сколько пользователей имеют строго больше очков
        return 1 + UserRating.objects.filter(points__gt=points).count()

    @extend_schema(
        summary="Полный рейтинг пользователей",
        description="Возвращает 3 блока: топ-3, текущий пользователь, все пользователи с 4-го места",
        parameters=[
            OpenApiParameter(
                name="current_user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID текущего пользователя (для блока current_user)",
                required=False,
            )
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=["Рейтинг пользователей"],
    )
    def list(self, request):
        current_user_id = request.query_params.get("current_user_id")

        # Топ-3
        top3_qs = UserRating.objects.select_related("user").order_by(
            "-points", "user_id"
        )[:3]
        top3_users = [ur.user for ur in top3_qs]

        def pack_user(u):
            return LeaderboardUserSerializer(u, context={"request": request}).data

        first_place = pack_user(top3_users[0]) if len(top3_users) > 0 else None
        second_place = pack_user(top3_users[1]) if len(top3_users) > 1 else None
        third_place = pack_user(top3_users[2]) if len(top3_users) > 2 else None

        # Текущий пользователь
        current_user_block = None
        if current_user_id:
            try:
                current_user = TelegramUser.objects.get(pk=current_user_id)
                points = (
                    getattr(getattr(current_user, "rating", None), "points", 0) or 0
                )
                place = self._get_place_for_points(points)
                current_user_block = {
                    "place": place,
                    "points": points,
                }
            except TelegramUser.DoesNotExist:
                current_user_block = None

        # Хвост с 4-го места
        exclude_ids = [u.id for u in top3_users]
        tail_qs = (
            TelegramUser.objects.select_related("rating")
            .filter(rating__isnull=False)
            .exclude(id__in=exclude_ids)
            .order_by("-rating__points", "id")
        )
        tail_data = LeaderboardUserSerializer(
            tail_qs, many=True, context={"request": request}
        ).data

        return Response(
            {
                "first_place": first_place,
                "second_place": second_place,
                "third_place": third_place,
                "current_user": current_user_block,
                "top_all_users": tail_data,
            }
        )

    # Эндпоинт по пользователю перенесён в статистику пользователя
