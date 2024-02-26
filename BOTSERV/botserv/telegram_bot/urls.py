from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ApplicationsViewsets, TelegramUserViewsets ###DirectoryServicesViewsets, BuildingEriellViewsets, FloorEriellViewsets, BlockEriellViewsets

router = DefaultRouter()
router.register(r'applications', ApplicationsViewsets)
router.register(r'telegramuser', TelegramUserViewsets)
# router.register(r'directoryservices', DirectoryServicesViewsets)
# router.register(r'buildingeriell', BuildingEriellViewsets)
# router.register(r'flooreriell', FloorEriellViewsets)
# router.register(r'blockeriell', BlockEriellViewsets)

urlpatterns = [
    path('', include(router.urls))
]