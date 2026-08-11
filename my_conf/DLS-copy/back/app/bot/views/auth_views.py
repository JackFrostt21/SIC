import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..serializers.auth_serializers import (
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
    AvatarUpdateSerializer,
)
from ..services.email_service import EmailService

logger = logging.getLogger(__name__)


class PasswordResetThrottle(AnonRateThrottle):
    """Кастомный throttle для сброса пароля - 3 попытки в час"""

    scope = "password_reset"


class LoginThrottle(AnonRateThrottle):
    """Кастомный throttle для логина - 10 попыток в час"""

    scope = "login"


class LoginView(APIView):
    """
    API endpoint для аутентификации пользователя.
    Поддерживает вход по email или username (включая TelegramUser.user_name).
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    @extend_schema(
        summary="Аутентификация пользователя",
        description="Аутентификация по email или username с возвратом JWT токенов и данных TelegramUser. Для админов/staff автоматически создается фиктивный TelegramUser при первом входе.",
        request=LoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "access_token": {"type": "string"},
                    "refresh_token": {"type": "string"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "telegram_user_id": {
                                "type": "integer",
                                "description": "ID записи TelegramUser",
                                "example": 47,
                            },
                            "telegram_id": {
                                "type": "integer",
                                "description": "Telegram ID пользователя (реальный или фиктивный)",
                                "example": 150000000005,
                            },
                            "username": {
                                "type": "string",
                                "description": "Имя пользователя в Telegram",
                                "example": "admin",
                            },
                            "full_name": {
                                "type": "string",
                                "description": "Полное имя пользователя",
                                "example": "Иванов Иван",
                            },
                            "email": {
                                "type": "string",
                                "description": "Email пользователя",
                                "example": "ivan.ivanov@cdtek.ru",
                            },
                            "phone": {
                                "type": "string",
                                "description": "Телефон пользователя",
                                "example": "+7(929)651-89-78",
                            },
                        },
                    },
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "errors": {"type": "object"},
                    "error": {
                        "type": "string",
                        "description": "Ошибка если пользователь не связан с Telegram аккаунтом",
                    },
                },
            },
            429: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        tags=["Аутентификация"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Проверяем связь с TelegramUser
            if not user.telegram_user:
                if user.is_superuser or user.is_staff:
                    # Создаем фиктивный TelegramUser для админа/staff
                    from ..models.telegram_user import TelegramUser

                    telegram_user = TelegramUser.objects.create(
                        telegram_id=150000000000
                        + user.id,  # 15 цифр - фиктивный Telegram ID
                        user_name=user.username,  # Из CustomUser
                        state=TelegramUser.STATE_NOT_ACTIVE,  # Неактивный статус
                    )

                    # Привязываем к CustomUser
                    user.telegram_user = telegram_user
                    user.save()

                    logger.info(
                        f"Создан фиктивный TelegramUser для {'суперпользователя' if user.is_superuser else 'сотрудника'}: {user.username} (Telegram ID: {telegram_user.telegram_id})"
                    )
                else:
                    # Обычные пользователи должны иметь реальную связь с Telegram
                    logger.warning(
                        f"Попытка входа пользователя без Telegram связи: {user.username}"
                    )
                    return Response(
                        {
                            "success": False,
                            "error": "Пользователь не связан с Telegram аккаунтом",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Связь юзера с телеграмюзером
            telegram_user = user.telegram_user

            # Генерируем JWT токены
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Логируем успешный вход
            logger.info(
                f"Успешная аутентификация пользователя: {user.username} (ID: {user.id})"
            )

            return Response(
                {
                    "success": True,
                    "message": "Аутентификация прошла успешно",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "telegram_user_id": telegram_user.id,
                        "telegram_id": telegram_user.telegram_id,
                        "username": telegram_user.user_name,
                        "full_name": telegram_user.full_name,
                        "email": telegram_user.email,
                        "phone": telegram_user.phone,
                    },
                },
                status=status.HTTP_200_OK,
            )

        # Логируем неудачную попытку
        login_field = request.data.get("login", "unknown")
        logger.warning(
            f"Неудачная попытка аутентификации: {login_field} с IP {request.META.get('REMOTE_ADDR')}"
        )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetRequestView(APIView):
    """
    API endpoint для запроса сброса пароля.
    Отправляет email с токеном для сброса.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    @extend_schema(
        summary="Запрос сброса пароля",
        description="Отправляет email с ссылкой для сброса пароля",
        request=PasswordResetRequestSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "errors": {"type": "object"},
                },
            },
            429: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        tags=["Аутентификация"],
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if serializer.is_valid():
            # Получаем IP адрес для логирования
            ip_address = request.META.get("REMOTE_ADDR")

            # Создаем токен сброса
            reset_token = serializer.save(ip_address=ip_address)

            # Отправляем email
            email_service = EmailService()
            user = reset_token.user

            # Определяем имя для приветствия
            user_name = user.first_name or user.username

            email_result = email_service.send_password_reset_email(
                user_email=user.email,
                reset_token=reset_token.token,
                user_name=user_name,
            )

            # Логируем запрос
            logger.info(
                f"Запрос сброса пароля для пользователя {user.email} с IP {ip_address}"
            )

            if email_result["success"]:
                return Response(
                    {
                        "success": True,
                        "message": "Инструкции по сбросу пароля отправлены на ваш email",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                logger.error(
                    f"Ошибка отправки email для сброса пароля: {email_result['message']}"
                )
                return Response(
                    {
                        "success": False,
                        "message": "Ошибка отправки email. Попробуйте позже.",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Логируем неудачную попытку
        email = request.data.get("email", "unknown")
        logger.warning(
            f"Неудачный запрос сброса пароля для {email} с IP {request.META.get('REMOTE_ADDR')}"
        )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetConfirmView(APIView):
    """
    API endpoint для подтверждения сброса пароля.
    Принимает токен и новый пароль.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    @extend_schema(
        summary="Подтверждение сброса пароля",
        description="Обновляет пароль пользователя по токену из email",
        request=PasswordResetConfirmSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "errors": {"type": "object"},
                },
            },
            429: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        tags=["Аутентификация"],
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            # Обновляем пароль
            user = serializer.save()

            # Логируем успешный сброс
            logger.info(
                f"Успешный сброс пароля для пользователя {user.username} (ID: {user.id})"
            )

            return Response(
                {
                    "success": True,
                    "message": "Пароль успешно обновлен. Теперь вы можете войти с новым паролем.",
                },
                status=status.HTTP_200_OK,
            )

        # Логируем неудачную попытку
        token = (
            request.data.get("token", "unknown")[:10] + "..."
        )  # Частично скрываем токен в логах
        logger.warning(
            f"Неудачная попытка сброса пароля с токеном {token} с IP {request.META.get('REMOTE_ADDR')}"
        )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordChangeView(APIView):
    """
    API endpoint для смены пароля аутентифицированного пользователя.
    Требует указания старого пароля для безопасности.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [PasswordResetThrottle]  # Используем тот же throttle

    @extend_schema(
        summary="Смена пароля",
        description="Позволяет аутентифицированному пользователю сменить пароль. Требует указания текущего пароля для безопасности.",
        request=PasswordChangeSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "errors": {"type": "object"},
                },
            },
            401: {"type": "object", "properties": {"detail": {"type": "string"}}},
            429: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        tags=["Аутентификация"],
    )
    def post(self, request):
        """
        Смена пароля пользователя.

        Требует:
        - old_password: текущий пароль
        - new_password: новый пароль
        - confirm_password: подтверждение нового пароля
        """
        # Создаем сериализатор с текущим пользователем в контексте
        serializer = PasswordChangeSerializer(data=request.data, user=request.user)

        if serializer.is_valid():
            # Обновляем пароль
            user = serializer.save()

            # Логируем успешную смену пароля
            logger.info(
                f"Успешная смена пароля для пользователя {user.username} (ID: {user.id}) "
                f"с IP {request.META.get('REMOTE_ADDR')}"
            )

            return Response(
                {
                    "success": True,
                    "message": "Пароль успешно изменен.",
                },
                status=status.HTTP_200_OK,
            )

        # Логируем неудачную попытку
        logger.warning(
            f"Неудачная попытка смены пароля для пользователя {request.user.username} "
            f"с IP {request.META.get('REMOTE_ADDR')}: {serializer.errors}"
        )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AvatarUpdateView(APIView):
    """
    API endpoint для обновления аватарки пользователя.
    Принимает файл изображения и обновляет поле image в TelegramUser.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Обновление аватарки пользователя",
        description="Загружает новую аватарку пользователя (jpg, jpeg, png, webp, до 2MB). Для админов/staff автоматически создается фиктивный TelegramUser при первом обращении.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "avatar": {
                        "type": "string",
                        "format": "binary",
                        "description": "Файл изображения (jpg, jpeg, png, webp, до 2MB)",
                    }
                },
                "required": ["avatar"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "telegram_user_id": {
                        "type": "integer",
                        "description": "ID записи TelegramUser",
                        "example": 47,
                    },
                    "avatar_url": {
                        "type": "string",
                        "description": "URL загруженной аватарки",
                        "example": "/media/telegramuser/avatar.jpg",
                    },
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "errors": {"type": "object"},
                    "message": {
                        "type": "string",
                        "description": "Ошибка валидации или отсутствие связанного Telegram профиля",
                    },
                },
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                },
            },
        },
        tags=["Аутентификация"],
    )
    def put(self, request):
        serializer = AvatarUpdateSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Обновляем аватарку
                telegram_user = serializer.save(user=request.user)

                # Получаем URL новой аватарки
                avatar_url = (
                request.build_absolute_uri(telegram_user.image.url) 
                if telegram_user.image 
                else None
                )

                # Логируем успешное обновление
                logger.info(
                    f"Пользователь {request.user.username} (ID: {request.user.id}) обновил аватарку"
                )

                return Response(
                    {
                        "success": True,
                        "message": "Аватарка успешно обновлена",
                        "telegram_user_id": telegram_user.id,
                        "avatar_url": avatar_url,
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                # Логируем ошибку
                logger.error(
                    f"Ошибка при обновлении аватарки для пользователя {request.user.username}: {str(e)}"
                )

                return Response(
                    {
                        "success": False,
                        "message": "Ошибка при сохранении аватарки. Попробуйте позже.",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Логируем неудачную попытку
        logger.warning(
            f'Неудачная попытка загрузки аватарки пользователем {request.user.username} с IP {request.META.get("REMOTE_ADDR")}'
        )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Поддерживаем также PATCH запросы
    patch = put
