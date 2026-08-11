from rest_framework import serializers
from ...bot.models.education_data import UserTest


class UserTestItemSerializer(serializers.Serializer):
    """
    Сериализует одну запись UserTest:
    - training_id — ID курса
    - training_title — заголовок курса
    - quantity_correct — процент правильных ответов
    - complete — флаг успешного прохождения
    """
    training_id = serializers.IntegerField(source='training.id')
    training_title = serializers.CharField(source='training.title')
    quantity_correct = serializers.IntegerField()
    complete = serializers.BooleanField()

class UserTestListSerializer(serializers.Serializer):
    """
    Обёртка для списка тестов одного пользователя:
    - telegram_user_id — ID Telegram-пользователя
    - full_name — полное имя или логин
    - tests — список записей, сериализованных через UserTestItemSerializer
    """
    telegram_user_id = serializers.IntegerField()
    full_name = serializers.CharField()
    tests = UserTestItemSerializer(many=True)