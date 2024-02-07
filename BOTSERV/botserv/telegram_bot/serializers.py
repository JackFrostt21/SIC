from rest_framework import serializers
from .models import Applications, TelegramUser

class ApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applications
        fields = [
            'user_eriell', 'name_services', 'building', 'floor', 'block', 'office_workplace',
              'internal_number', 'mobile_phone', 'application_text'
        ]


class TelegramUserSerializer(serializers.ModelSerializer):
    user_eriell = serializers.CharField(required=False)
    internal_number = serializers.CharField(required=False)
    mobile_phone = serializers.CharField(required=False)

    class Meta:
        model = TelegramUser
        fields = [
            'user_eriell', 'email', 'username_telegram', 'internal_number', 'mobile_phone'
        ]