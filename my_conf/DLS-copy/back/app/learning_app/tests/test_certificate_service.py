from datetime import date
from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from PIL import Image

from app.bot.models import CustomUser, TelegramUser
from app.learning_app.models import Certificate, TrainingCourse
from app.learning_app.services.certificate_renderer import (
    CertificateRenderingError,
    PdfCertificateRenderer,
)
from app.learning_app.services.certificate_service import (
    CertificateIssuanceError,
    CertificateIssueStatus,
    CertificateService,
)
from app.organization.models import Company


class CertificateServiceTests(TestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.media_override.enable()

        self.author = CustomUser.objects.create_user(
            username="certificate-author",
            password="test-password",
        )
        self.company = Company.objects.create(name="Тестовая компания")
        self.template_bytes = self._make_template()
        self.company.certificate_template.save(
            "template.png",
            ContentFile(self.template_bytes),
        )
        self.user = TelegramUser.objects.create(
            telegram_id=101,
            company=self.company,
            full_name="  Иванов   Иван Иванович  ",
        )
        self.course = TrainingCourse.objects.create(
            title="  Охрана   труда  ",
            author=self.author,
            certificate_validity_days=365,
        )
        self.renderer = Mock(spec=PdfCertificateRenderer)
        self.renderer.render.return_value = b"%PDF-1.4 test certificate"
        self.service = CertificateService(renderer=self.renderer)
        self.completed_at = date(2026, 8, 5)

    def tearDown(self):
        self.media_override.disable()
        self.media_directory.cleanup()

    def test_successful_attempt_creates_certificate_and_file(self):
        result = self._issue()

        self.assertEqual(result.status, CertificateIssueStatus.CREATED)
        certificate = Certificate.objects.get(pk=result.certificate_id)
        self.assertEqual(certificate.user, self.user)
        self.assertEqual(certificate.training_course, self.course)
        self.assertEqual(certificate.recipient_name, "Иванов Иван Иванович")
        self.assertEqual(certificate.course_title, "Охрана труда")
        self.assertEqual(certificate.result, 95)
        self.assertEqual(certificate.completed_at, self.completed_at)
        self.assertEqual(certificate.expires_at, date(2027, 8, 5))
        self.assertTrue(certificate.certificate_file.name.startswith("certificates/"))
        with certificate.certificate_file.open("rb") as certificate_file:
            self.assertEqual(certificate_file.read(), self.renderer.render.return_value)
        self.renderer.render.assert_called_once_with(
            template_bytes=self.template_bytes,
            recipient_name="Иванов Иван Иванович",
            course_title="Охрана труда",
            completed_at=self.completed_at,
        )

    def test_repeated_attempt_returns_existing_immutable_certificate(self):
        first_result = self._issue(score=95)
        self.user.full_name = "Петров Пётр Петрович"
        self.user.save(update_fields=["full_name"])
        self.course.title = "Новое название курса"
        self.course.save(update_fields=["title"])
        self.company.certificate_template.delete(save=True)

        second_result = self._issue(score=100)

        self.assertEqual(second_result.status, CertificateIssueStatus.EXISTING)
        self.assertEqual(second_result.certificate_id, first_result.certificate_id)
        self.assertEqual(Certificate.objects.count(), 1)
        certificate = Certificate.objects.get(pk=first_result.certificate_id)
        self.assertEqual(certificate.recipient_name, "Иванов Иван Иванович")
        self.assertEqual(certificate.course_title, "Охрана труда")
        self.assertEqual(certificate.result, 95)
        self.assertEqual(self.renderer.render.call_count, 1)

    def test_existing_unfinished_certificate_returns_pending(self):
        certificate = Certificate.objects.create(
            user=self.user,
            training_course=self.course,
            recipient_name="Иванов Иван Иванович",
            course_title="Охрана труда",
            result=95,
            completed_at=self.completed_at,
            expires_at=date(2027, 8, 5),
        )

        result = self._issue()

        self.assertEqual(result.status, CertificateIssueStatus.PENDING)
        self.assertEqual(result.certificate_id, certificate.pk)
        self.assertEqual(result.reason, "generation_in_progress")
        self.renderer.render.assert_not_called()

    def test_failed_attempt_is_skipped(self):
        result = self._issue(score=89, passed=False)

        self.assertEqual(result.status, CertificateIssueStatus.SKIPPED)
        self.assertEqual(result.reason, "attempt_not_passed")
        self.assertFalse(Certificate.objects.exists())
        self.renderer.render.assert_not_called()

    def test_course_without_validity_period_is_skipped(self):
        self.course.certificate_validity_days = None
        self.course.save(update_fields=["certificate_validity_days"])

        result = self._issue()

        self.assertEqual(result.status, CertificateIssueStatus.SKIPPED)
        self.assertEqual(result.reason, "course_certificate_disabled")
        self.assertFalse(Certificate.objects.exists())

    def test_user_without_company_is_skipped(self):
        self.user.company = None
        self.user.save(update_fields=["company"])

        result = self._issue()

        self.assertEqual(result.status, CertificateIssueStatus.SKIPPED)
        self.assertEqual(result.reason, "company_missing")
        self.assertFalse(Certificate.objects.exists())

    def test_company_without_template_is_skipped(self):
        self.company.certificate_template.delete(save=True)

        result = self._issue()

        self.assertEqual(result.status, CertificateIssueStatus.SKIPPED)
        self.assertEqual(result.reason, "template_missing")
        self.assertFalse(Certificate.objects.exists())

    def test_user_without_full_name_is_skipped(self):
        self.user.full_name = None
        self.user.save(update_fields=["full_name"])

        result = self._issue()

        self.assertEqual(result.status, CertificateIssueStatus.SKIPPED)
        self.assertEqual(result.reason, "recipient_name_missing")
        self.assertFalse(Certificate.objects.exists())

    def test_render_error_removes_unfinished_row_and_allows_retry(self):
        self.renderer.render.side_effect = CertificateRenderingError("broken template")

        with self.assertLogs(
            "app.learning_app.services.certificate_service",
            level="ERROR",
        ):
            failed_result = self._issue()

        self.assertEqual(failed_result.status, CertificateIssueStatus.FAILED)
        self.assertEqual(failed_result.reason, "render_failed")
        self.assertFalse(Certificate.objects.exists())

        self.renderer.render.side_effect = None
        retry_result = self._issue()

        self.assertEqual(retry_result.status, CertificateIssueStatus.CREATED)
        self.assertEqual(Certificate.objects.count(), 1)

    def test_storage_error_removes_unfinished_row(self):
        storage = Certificate._meta.get_field("certificate_file").storage
        with self.assertLogs(
            "app.learning_app.services.certificate_service",
            level="ERROR",
        ):
            with patch.object(
                storage,
                "save",
                side_effect=OSError("storage unavailable"),
            ):
                result = self._issue()

        self.assertEqual(result.status, CertificateIssueStatus.FAILED)
        self.assertEqual(result.reason, "storage_failed")
        self.assertFalse(Certificate.objects.exists())

    def test_invalid_score_is_rejected_as_programmer_error(self):
        with self.assertRaisesMessage(
            CertificateIssuanceError,
            "attempt_score",
        ):
            self._issue(score=101)

        self.assertFalse(Certificate.objects.exists())

    def _issue(self, *, score=95, passed=True):
        return self.service.issue_for_course_attempt(
            user_id=self.user.pk,
            course_id=self.course.pk,
            attempt_score=score,
            attempt_passed=passed,
            completed_at=self.completed_at,
        )

    @staticmethod
    def _make_template() -> bytes:
        output = BytesIO()
        image = Image.new("RGB", (1061, 1483), "white")
        image.save(output, format="PNG")
        image.close()
        return output.getvalue()
