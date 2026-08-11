from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ..views.userstat_views import UserStatsViewSet

router = DefaultRouter()
router.register(r"user-stats", UserStatsViewSet, basename="userstats")

urlpatterns = [
    path("", include(router.urls)),
]
