from rest_framework import routers
from django.urls import path
from app.lightning.views import lightnings_custom_view, LightningDeleteView, send_lightning_view


router = routers.DefaultRouter()

urlpatterns = [
    *router.urls,

    path("lightnings/", lightnings_custom_view, name="lightning_custom"),
    path("lightning/<int:lightning_id>/", lightnings_custom_view, name="lightning_custom"),
    path('lightnings/create/', lightnings_custom_view, name='lightning_custom_create'),
    path('lightning/<int:pk>/delete/', LightningDeleteView.as_view(), name='lightning_delete'),
    path('ru/send_lightning/<int:lightning_id>/', send_lightning_view, name='send_lightning'),
]