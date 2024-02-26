from rest_framework import viewsets, permissions
from .models import Applications, TelegramUser  ###DirectoryServices, BuildingEriell, FloorEriell, BlockEriell, 
from .serializers import ApplicationsSerializer, TelegramUserSerializer ###DirectoryServicesSerializer, BuildingEriellSerializer, FloorEriellSerializer, BlockEriellSerializer, 

class ApplicationsViewsets(viewsets.ModelViewSet):
    queryset = Applications.objects.all()
    serializer_class = ApplicationsSerializer
    permission_classes = [permissions.IsAuthenticated]

class TelegramUserViewsets(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [permissions.IsAuthenticated]

# class DirectoryServicesViewsets(viewsets.ModelViewSet):
#     queryset = DirectoryServices.objects.all()
#     serializer_class = DirectoryServicesSerializer
#     permission_classes = [permissions.IsAuthenticated]

# class BuildingEriellViewsets(viewsets.ModelViewSet):
#     queryset = BuildingEriell.objects.all()
#     serializer_class = BuildingEriellSerializer
#     permission_classes = [permissions.IsAuthenticated]
    

# class FloorEriellViewsets(viewsets.ModelViewSet):
#     queryset = FloorEriell.objects.all()
#     serializer_class = FloorEriellSerializer
#     permission_classes = [permissions.IsAuthenticated]

# class BlockEriellViewsets(viewsets.ModelViewSet):
#     queryset = BlockEriell.objects.all()
#     serializer_class = BlockEriellSerializer
#     permission_classes = [permissions.IsAuthenticated]