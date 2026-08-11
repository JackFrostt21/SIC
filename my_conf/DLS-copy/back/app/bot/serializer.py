from rest_framework import serializers

from app.learning_app.models import Certificate

from .models.education_data import UserRead, UserTest
from .models.telegram_user import TelegramUser, TelegramGroup, CustomUser


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRead
        fields = "__all__"


class UserTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTest
        fields = "__all__"


class TelegramUserCertificateSerializer(serializers.ModelSerializer):
    """Краткие данные сертификата для web-профиля пользователя."""

    class Meta:
        model = Certificate
        fields = [
            "id",
            "training_course",
            "recipient_name",
            "course_title",
            "result",
            "completed_at",
            "expires_at",
            "certificate_file",
        ]
        read_only_fields = fields


class TelegramUserSerializer(serializers.ModelSerializer):
    certificates = TelegramUserCertificateSerializer(many=True, read_only=True)

    class Meta:
        model = TelegramUser
        fields = "__all__"


class TelegramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramGroup
        fields = "__all__"


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
