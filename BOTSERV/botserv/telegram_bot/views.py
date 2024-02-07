from rest_framework import viewsets, permissions
from .models import Applications, TelegramUser
from .serializers import ApplicationsSerializer, TelegramUserSerializer

class ApplicationsViewsets(viewsets.ModelViewSet):
    queryset = Applications.objects.all()
    serializer_class = ApplicationsSerializer

class TelegramUserViewsets(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer


# permissions - почитать!
   # permission_classes = (IsAuthenticated,)