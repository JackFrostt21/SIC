import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class EmailService:
    """
    Сервис для отправки email уведомлений.
    Поддерживает различные типы писем с простыми текстовыми шаблонами.
    """

    def __init__(self):
        self.from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
        self.frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")

    def send_password_reset_email(
        self, user_email: str, reset_token: str, user_name: str = None
    ) -> Dict[str, Any]:
        """
        Отправляет письмо для сброса пароля.

        :param user_email: Email получателя
        :param reset_token: Токен для сброса пароля
        :param user_name: Имя пользователя (опционально)
        :return: Результат отправки
        """
        try:
            # Определяем обращение к пользователю
            greeting = f"Здравствуйте, {user_name}!" if user_name else "Здравствуйте!"

            # Текст письма
            subject = "Сброс пароля - СДО"
            message = self._get_password_reset_message(greeting, reset_token)

            # Отправляем письмо
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[user_email],
                fail_silently=False,
            )

            logger.info(f"Письмо сброса пароля отправлено на {user_email}")
            return {"success": True, "message": "Письмо успешно отправлено"}

        except Exception as e:
            logger.error(f"Ошибка отправки письма на {user_email}: {str(e)}")
            return {"success": False, "message": f"Ошибка отправки письма: {str(e)}"}

    def _get_password_reset_message(self, greeting: str, reset_token: str) -> str:
        """Формирует текст письма для сброса пароля"""
        return f"""{greeting}

Вы запросили сброс пароля для вашего аккаунта в системе дистанционного обучения (СДО).

Ваш токен для сброса пароля:
{reset_token}

Скопируйте токен и вставьте его в поле ввода на странице сброса пароля.


Важная информация:
• Токен действителен в течение 1 часа
• После использования токен станет недействительным
• Если вы не запрашивали сброс пароля, проигнорируйте это письмо

Если у вас возникли вопросы, обратитесь к администратору системы.

--
С уважением,
Команда СДО"""

    def send_test_email(self, recipient_email: str) -> Dict[str, Any]:
        """
        Отправляет тестовое письмо для проверки настроек.

        :param recipient_email: Email получателя
        :return: Результат отправки
        """
        try:
            subject = "Тест отправки email - СДО"
            message = """Это тестовое письмо из системы дистанционного обучения (СДО).

Если вы получили это письмо, значит настройки email работают корректно.

--
Команда СДО"""

            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[recipient_email],
                fail_silently=False,
            )

            logger.info(f"Тестовое письмо отправлено на {recipient_email}")
            return {"success": True, "message": "Тестовое письмо успешно отправлено"}

        except Exception as e:
            logger.error(
                f"Ошибка отправки тестового письма на {recipient_email}: {str(e)}"
            )
            return {"success": False, "message": f"Ошибка отправки письма: {str(e)}"}

    def get_email_settings_status(self) -> Dict[str, Any]:
        """
        Проверяет настройки email.

        :return: Статус настроек
        """
        required_settings = [
            "EMAIL_HOST",
            "EMAIL_PORT",
            "EMAIL_HOST_USER",
            "EMAIL_HOST_PASSWORD",
        ]

        missing_settings = []
        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                missing_settings.append(setting)

        if missing_settings:
            return {
                "configured": False,
                "missing_settings": missing_settings,
                "message": f'Отсутствуют настройки: {", ".join(missing_settings)}',
            }

        return {
            "configured": True,
            "email_backend": getattr(settings, "EMAIL_BACKEND", "Не настроен"),
            "email_host": getattr(settings, "EMAIL_HOST", "Не настроен"),
            "email_port": getattr(settings, "EMAIL_PORT", "Не настроен"),
            "from_email": self.from_email,
            "frontend_url": self.frontend_url,
            "message": "Email настроен корректно",
        }
