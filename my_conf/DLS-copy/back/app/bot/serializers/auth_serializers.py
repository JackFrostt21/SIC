from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from app.bot.models import CustomUser, TelegramUser, PasswordResetToken


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для аутентификации пользователя.
    Поддерживает вход по email или username (в том числе через TelegramUser.user_name).
    """

    login = serializers.CharField(
        max_length=255, help_text="Email или username пользователя"
    )
    password = serializers.CharField(
        max_length=128,
        style={"input_type": "password"},
        help_text="Пароль пользователя",
    )

    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")

        if not login or not password:
            raise serializers.ValidationError("Необходимо указать логин и пароль.")

        # Попытка найти пользователя по разным полям
        user = self._find_user(login)

        if not user:
            raise serializers.ValidationError(
                "Пользователь с указанными данными не найден."
            )

        # Проверяем активность пользователя
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт пользователя деактивирован.")

        # Проверяем пароль
        if not user.check_password(password):
            raise serializers.ValidationError("Неверный пароль.")

        attrs["user"] = user
        return attrs

    def _find_user(self, login):
        """
        Ищет пользователя по различным полям:
        1. Email в CustomUser
        2. Username в CustomUser
        3. user_name в TelegramUser (через связь)
        """
        user = None

        # 1. Поиск по email в CustomUser
        try:
            user = CustomUser.objects.get(email=login)
        except CustomUser.DoesNotExist:
            pass

        # 2. Поиск по username в CustomUser
        if not user:
            try:
                user = CustomUser.objects.get(username=login)
            except CustomUser.DoesNotExist:
                pass

        # 3. Поиск через TelegramUser.user_name
        if not user:
            try:
                telegram_user = TelegramUser.objects.get(user_name=login)
                if hasattr(telegram_user, "custom_user") and telegram_user.custom_user:
                    user = telegram_user.custom_user
            except TelegramUser.DoesNotExist:
                pass

        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Сериализатор для запроса сброса пароля.
    """

    email = serializers.EmailField(help_text="Email пользователя для сброса пароля")

    def validate_email(self, value):
        """Проверяем существование пользователя с данным email"""
        try:
            user = CustomUser.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError("Аккаунт пользователя деактивирован.")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                "Пользователь с указанным email не найден."
            )

        return value

    def save(self, **kwargs):
        """Создает токен сброса пароля"""
        email = self.validated_data["email"]
        user = CustomUser.objects.get(email=email)

        # Инвалидируем все предыдущие токены пользователя
        PasswordResetToken.invalidate_user_tokens(user)

        # Создаем новый токен
        reset_token = PasswordResetToken.objects.create(
            user=user, ip_address=kwargs.get("ip_address")
        )

        return reset_token


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля.
    """

    token = serializers.CharField(
        max_length=255, help_text="Токен сброса пароля из письма"
    )
    new_password = serializers.CharField(
        max_length=128, style={"input_type": "password"}, help_text="Новый пароль"
    )
    new_password_confirm = serializers.CharField(
        max_length=128,
        style={"input_type": "password"},
        help_text="Подтверждение нового пароля",
    )

    def validate_token(self, value):
        """Проверяем валидность токена"""
        try:
            reset_token = PasswordResetToken.objects.get(token=value)

            if not reset_token.is_valid():
                if reset_token.is_used:
                    raise serializers.ValidationError("Токен уже был использован.")
                else:
                    raise serializers.ValidationError(
                        "Токен истек. Запросите новый сброс пароля."
                    )

        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Недействительный токен.")

        return value

    def validate_new_password(self, value):
        """Валидируем новый пароль"""
        try:
            validate_password(value)
        except ValidationError as error:
            raise serializers.ValidationError(error.messages)
        return value

    def validate(self, attrs):
        """Проверяем совпадение паролей"""
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {"new_password_confirm": "Пароли не совпадают."}
            )

        return attrs

    def save(self, **kwargs):
        """Обновляет пароль пользователя"""
        token_string = self.validated_data["token"]
        new_password = self.validated_data["new_password"]

        # Получаем токен (мы уже проверили его в validate_token)
        reset_token = PasswordResetToken.objects.get(token=token_string)

        # Обновляем пароль
        user = reset_token.user
        user.set_password(new_password)
        user.save()

        # Помечаем токен как использованный
        reset_token.mark_as_used()

        return user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Сериализатор для смены пароля аутентифицированного пользователя.
    """

    old_password = serializers.CharField(
        max_length=128,
        style={"input_type": "password"},
        help_text="Текущий пароль пользователя",
    )
    new_password = serializers.CharField(
        max_length=128,
        style={"input_type": "password"},
        help_text="Новый пароль",
    )
    confirm_password = serializers.CharField(
        max_length=128,
        style={"input_type": "password"},
        help_text="Подтверждение нового пароля",
    )

    def __init__(self, *args, **kwargs):
        """Получаем пользователя из контекста"""
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def validate_old_password(self, value):
        """Проверяем правильность текущего пароля"""
        if not self.user:
            raise serializers.ValidationError("Пользователь не найден в контексте.")

        if not self.user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль.")

        return value

    def validate_new_password(self, value):
        """Валидируем новый пароль"""
        try:
            validate_password(value, user=self.user)
        except ValidationError as error:
            raise serializers.ValidationError(error.messages)
        return value

    def validate(self, attrs):
        """Проверяем совпадение нового пароля и подтверждения"""
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Пароли не совпадают."}
            )

        # Проверяем, что новый пароль отличается от старого
        old_password = attrs.get("old_password")
        if new_password == old_password:
            raise serializers.ValidationError(
                {"new_password": "Новый пароль должен отличаться от текущего."}
            )

        return attrs

    def save(self, **kwargs):
        """Обновляет пароль пользователя"""
        new_password = self.validated_data["new_password"]

        # Обновляем пароль
        self.user.set_password(new_password)
        self.user.save()

        return self.user


class AvatarUpdateSerializer(serializers.Serializer):
    """
    Сериализатор для обновления аватарки пользователя.
    """

    avatar = serializers.ImageField(
        help_text="Файл изображения для аватарки (jpg, jpeg, png, webp, до 2MB)"
    )

    def validate_avatar(self, value):
        """Валидируем загруженное изображение"""
        # Проверяем размер файла (2MB = 2 * 1024 * 1024 bytes)
        max_size = 2 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("Размер файла не должен превышать 2MB.")

        # Проверяем формат файла
        allowed_formats = ["jpeg", "jpg", "png", "webp"]
        file_extension = value.name.split(".")[-1].lower()

        if file_extension not in allowed_formats:
            raise serializers.ValidationError(
                f'Недопустимый формат файла. Разрешены: {", ".join(allowed_formats)}'
            )

        return value

    def save(self, user):
        """Обновляет аватарку пользователя"""
        avatar_file = self.validated_data["avatar"]

        # Получаем связанного TelegramUser
        telegram_user = user.telegram_user

        # Если нет связанного TelegramUser, создаем фиктивный для админов/staff
        if not telegram_user:
            if user.is_superuser or user.is_staff:
                # Создаем фиктивный TelegramUser для админа/staff
                from app.bot.models.telegram_user import TelegramUser

                telegram_user = TelegramUser.objects.create(
                    telegram_id=150000000000 + user.id,  # 15 цифр - фиктивный Telegram ID
                    user_name=user.username,  # Из CustomUser
                    state=TelegramUser.STATE_NOT_ACTIVE,  # Неактивный статус
                )

                # Привязываем к CustomUser
                user.telegram_user = telegram_user
                user.save()
            else:
                # Обычные пользователи должны иметь реальную связь с Telegram
                raise serializers.ValidationError(
                    "У пользователя нет связанного Telegram профиля."
                )

        # # Сохраняем старый файл для удаления
        # old_avatar = telegram_user.image

        # Обновляем аватарку
        telegram_user.image = avatar_file
        telegram_user.save()

        # # Опционально: удаляем старый файл
        # if old_avatar:
        #     old_avatar.delete(save=False)

        return telegram_user
