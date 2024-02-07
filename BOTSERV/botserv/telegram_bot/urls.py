from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ApplicationsViewsets, TelegramUserViewsets

router = DefaultRouter()
router.register(r'applications', ApplicationsViewsets)
router.register(r'telegramuser', TelegramUserViewsets)

urlpatterns = [
    path('', include(router.urls))
]


















