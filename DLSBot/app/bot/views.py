from django.shortcuts import render
from rest_framework import viewsets
from .models.telegram_user import TelegramUser, TelegramGroup
from .models.education_data import UserRead, UserTest
from .serializer import (
    TelegramUserSerializer,
    TelegramGroupSerializer,
    UserReadSerializer,
    UserTestSerializer,
)


class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer


class TelegramGroupViewSet(viewsets.ModelViewSet):
    queryset = TelegramGroup.objects.all()
    serializer_class = TelegramGroupSerializer


class UserReadViewSet(viewsets.ModelViewSet):
    queryset = UserRead.objects.all()
    serializer_class = UserReadSerializer


class UserTestViewSet(viewsets.ModelViewSet):
    queryset = UserTest.objects.all()
    serializer_class = UserTestSerializer
