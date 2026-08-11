from rest_framework import serializers

from app.bot.models.telegram_user import TelegramUser


class LeaderboardUserSerializer(serializers.ModelSerializer):
    avatarka = serializers.SerializerMethodField()
    FIO = serializers.SerializerMethodField()
    points = serializers.IntegerField(source="rating.points", default=0)

    class Meta:
        model = TelegramUser
        fields = ["id", "avatarka", "FIO", "points"]

    def get_avatarka(self, obj):
        if not getattr(obj, "image", None):
            return None
        # Получаем request из контекста и строим абсолютный URL
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_FIO(self, obj):
        full_name = (obj.full_name or "").strip()
        if full_name:
            return full_name
        parts = [p for p in [obj.last_name, obj.first_name, obj.middle_name] if p]
        return " ".join(parts).strip()
