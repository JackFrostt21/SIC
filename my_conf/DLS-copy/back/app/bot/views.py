# Импортируем все views из новой структуры для обратной совместимости
from .views.viewsets import (
    TelegramUserViewSet,
    TelegramGroupViewSet,
    UserReadViewSet,
    UserTestViewSet,
)
from .views.auth_views import (
    LoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
