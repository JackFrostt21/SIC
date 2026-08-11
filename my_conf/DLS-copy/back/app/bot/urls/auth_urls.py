from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from ..views.auth_views import (
    LoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView,
    AvatarUpdateView,
)

urlpatterns = [
    # Аутентификация
    path("login/", LoginView.as_view(), name="auth_login"),
    # Обновление токена
    path("refresh/", TokenRefreshView.as_view(), name="auth_refresh"),
    # Сброс пароля
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Смена пароля
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    # Обновление аватарки
    path("avatar/", AvatarUpdateView.as_view(), name="avatar_update"),
]
