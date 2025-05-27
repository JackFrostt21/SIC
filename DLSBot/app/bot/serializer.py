from rest_framework import serializers
from .models.education_data import UserRead, UserTest
from .models.telegram_user import TelegramUser, TelegramGroup


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRead
        fields = '__all__'  


class UserTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTest
        fields = '__all__'  


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = '__all__'  


class TelegramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramGroup
        fields = '__all__'  
