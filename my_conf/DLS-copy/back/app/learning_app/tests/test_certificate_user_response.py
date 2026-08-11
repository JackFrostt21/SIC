from datetime import date
from tempfile import TemporaryDirectory

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from app.bot.models import CustomUser, TelegramUser
from app.learning_app.models import Certificate, TrainingCourse


class TelegramUserCertificateResponseTests(TestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.media_override.enable()

        self.telegram_user = TelegramUser.objects.create(
            telegram_id=101,
            full_name="Иванов Иван Иванович",
        )
        self.auth_user = CustomUser.objects.create_user(
            username="certificate-user",
            password="test-password",
            telegram_user=self.telegram_user,
        )
        self.course = TrainingCourse.objects.create(
            title="Охрана труда",
            author=self.auth_user,
            certificate_validity_days=365,
        )
        self.certificate = Certificate.objects.create(
            user=self.telegram_user,
            training_course=self.course,
            recipient_name="Иванов Иван Иванович",
            course_title="Охрана труда",
            result=95,
            completed_at=date(2026, 8, 6),
            expires_at=date(2027, 8, 6),
        )
        self.certificate.certificate_file.save(
            "certificate.pdf",
            ContentFile(b"%PDF-1.4 test certificate"),
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.auth_user)
        self.url = reverse(
            "web_telegramuser-detail",
            kwargs={"pk": self.telegram_user.pk},
        )

    def tearDown(self):
        self.media_override.disable()
        self.media_directory.cleanup()

    def test_user_response_contains_certificate_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.telegram_user.pk)
        self.assertEqual(len(response.data["certificates"]), 1)

        certificate_data = response.data["certificates"][0]
        self.assertEqual(certificate_data["id"], self.certificate.pk)
        self.assertEqual(certificate_data["training_course"], self.course.pk)
        self.assertEqual(certificate_data["recipient_name"], "Иванов Иван Иванович")
        self.assertEqual(certificate_data["course_title"], "Охрана труда")
        self.assertEqual(certificate_data["result"], 95)
        self.assertEqual(certificate_data["completed_at"], "2026-08-06")
        self.assertEqual(certificate_data["expires_at"], "2027-08-06")
        self.assertTrue(
            certificate_data["certificate_file"].endswith(
                "/media/certificates/certificate.pdf"
            )
        )

    def test_user_response_contains_empty_list_without_certificates(self):
        self.certificate.certificate_file.delete(save=False)
        self.certificate.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["certificates"], [])
