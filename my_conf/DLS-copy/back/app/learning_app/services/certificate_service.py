import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from uuid import uuid4

from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.db import DatabaseError, IntegrityError, transaction

from app.bot.models import TelegramUser
from app.learning_app.models import Certificate, TrainingCourse
from app.learning_app.services.certificate_renderer import PdfCertificateRenderer


class CertificateIssuanceError(ValueError):
    """Raised when the caller supplies an invalid course-attempt context."""


class CertificateIssueStatus(str, Enum):
    CREATED = "created"
    EXISTING = "existing"
    SKIPPED = "skipped"
    PENDING = "pending"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class CertificateIssueResult:
    status: CertificateIssueStatus
    certificate_id: int | None = None
    reason: str | None = None

    def as_dict(self) -> dict[str, int | str | None]:
        return {
            "status": self.status.value,
            "id": self.certificate_id,
            "reason": self.reason,
        }


class CertificateService:
    """Issue one immutable certificate for a successful course attempt."""

    def __init__(self, renderer: PdfCertificateRenderer | None = None):
        self.renderer = renderer or PdfCertificateRenderer()
        self.logger = logging.getLogger(__name__)

    async def aissue_for_course_attempt(
        self,
        *,
        user_id: int,
        course_id: int,
        attempt_score: int,
        attempt_passed: bool,
        completed_at: date,
    ) -> CertificateIssueResult:
        """Run the synchronous ORM and storage workflow outside the event loop."""
        return await sync_to_async(
            self.issue_for_course_attempt,
            thread_sensitive=True,
        )(
            user_id=user_id,
            course_id=course_id,
            attempt_score=attempt_score,
            attempt_passed=attempt_passed,
            completed_at=completed_at,
        )

    def issue_for_course_attempt(
        self,
        *,
        user_id: int,
        course_id: int,
        attempt_score: int,
        attempt_passed: bool,
        completed_at: date,
    ) -> CertificateIssueResult:
        """Issue or return a certificate for the current trusted attempt."""
        self._validate_attempt_context(
            user_id=user_id,
            course_id=course_id,
            attempt_score=attempt_score,
            attempt_passed=attempt_passed,
            completed_at=completed_at,
        )
        if not attempt_passed:
            return CertificateIssueResult(
                status=CertificateIssueStatus.SKIPPED,
                reason="attempt_not_passed",
            )

        try:
            existing_certificate = (
                Certificate.objects.only("id", "certificate_file")
                .filter(user_id=user_id, training_course_id=course_id)
                .first()
            )
            if existing_certificate:
                return self._result_for_existing(existing_certificate)

            course = TrainingCourse.objects.only(
                "id",
                "title",
                "certificate_validity_days",
            ).get(pk=course_id)
            user = (
                TelegramUser.objects.select_related("company")
                .only(
                    "id",
                    "full_name",
                    "company_id",
                    "company__id",
                    "company__certificate_template",
                )
                .get(pk=user_id)
            )
        except TrainingCourse.DoesNotExist:
            return CertificateIssueResult(
                status=CertificateIssueStatus.FAILED,
                reason="course_not_found",
            )
        except TelegramUser.DoesNotExist:
            return CertificateIssueResult(
                status=CertificateIssueStatus.FAILED,
                reason="user_not_found",
            )
        except DatabaseError:
            self.logger.exception(
                "Failed to load certificate context user_id=%s course_id=%s",
                user_id,
                course_id,
            )
            return CertificateIssueResult(
                status=CertificateIssueStatus.FAILED,
                reason="database_error",
            )

        validity_days = course.certificate_validity_days
        if not validity_days or validity_days < 1:
            return CertificateIssueResult(
                status=CertificateIssueStatus.SKIPPED,
                reason="course_certificate_disabled",
            )
        if not user.company_id:
            return CertificateIssueResult(
                status=CertificateIssueStatus.SKIPPED,
                reason="company_missing",
            )

        template_file = user.company.certificate_template
        if not template_file:
            return CertificateIssueResult(
                status=CertificateIssueStatus.SKIPPED,
                reason="template_missing",
            )

        recipient_name = self._normalize_snapshot(user.full_name)
        if not recipient_name:
            return CertificateIssueResult(
                status=CertificateIssueStatus.SKIPPED,
                reason="recipient_name_missing",
            )
        course_title = self._normalize_snapshot(course.title)
        if not course_title:
            return CertificateIssueResult(
                status=CertificateIssueStatus.FAILED,
                reason="course_title_missing",
            )

        try:
            template_bytes = self._read_template(template_file)
        except Exception:
            self.logger.exception(
                "Failed to read certificate template user_id=%s course_id=%s",
                user_id,
                course_id,
            )
            return CertificateIssueResult(
                status=CertificateIssueStatus.FAILED,
                reason="template_read_failed",
            )

        expires_at = completed_at + timedelta(days=validity_days)
        try:
            certificate, created = self._get_or_create_certificate(
                user_id=user_id,
                course_id=course_id,
                recipient_name=recipient_name,
                course_title=course_title,
                attempt_score=attempt_score,
                completed_at=completed_at,
                expires_at=expires_at,
            )
        except DatabaseError:
            self.logger.exception(
                "Failed to create certificate row user_id=%s course_id=%s",
                user_id,
                course_id,
            )
            return CertificateIssueResult(
                status=CertificateIssueStatus.FAILED,
                reason="database_error",
            )

        if not created:
            return self._result_for_existing(certificate)

        try:
            pdf_bytes = self.renderer.render(
                template_bytes=template_bytes,
                recipient_name=recipient_name,
                course_title=course_title,
                completed_at=completed_at,
            )
        except Exception:
            self.logger.exception(
                "Failed to render certificate certificate_id=%s user_id=%s course_id=%s",
                certificate.pk,
                user_id,
                course_id,
            )
            self._delete_unfinished_certificate(certificate.pk)
            return CertificateIssueResult(
                status=CertificateIssueStatus.FAILED,
                reason="render_failed",
            )

        return self._store_pdf(
            certificate=certificate,
            pdf_bytes=pdf_bytes,
            user_id=user_id,
            course_id=course_id,
        )

    def _store_pdf(
        self,
        *,
        certificate: Certificate,
        pdf_bytes: bytes,
        user_id: int,
        course_id: int,
    ) -> CertificateIssueResult:
        field = certificate.certificate_file.field
        storage = certificate.certificate_file.storage
        filename = f"certificate-{certificate.pk}-{uuid4().hex}.pdf"
        generated_name = field.generate_filename(certificate, filename)

        try:
            stored_name = storage.save(generated_name, ContentFile(pdf_bytes))
        except Exception:
            self.logger.exception(
                "Failed to store certificate certificate_id=%s user_id=%s course_id=%s",
                certificate.pk,
                user_id,
                course_id,
            )
            self._delete_unfinished_certificate(certificate.pk)
            return CertificateIssueResult(
                status=CertificateIssueStatus.FAILED,
                reason="storage_failed",
            )

        try:
            with transaction.atomic():
                locked_certificate = Certificate.objects.select_for_update().get(
                    pk=certificate.pk
                )
                if locked_certificate.certificate_file:
                    result = CertificateIssueResult(
                        status=CertificateIssueStatus.EXISTING,
                        certificate_id=locked_certificate.pk,
                    )
                else:
                    locked_certificate.certificate_file.name = stored_name
                    locked_certificate.save(
                        update_fields=["certificate_file", "updated_at"]
                    )
                    result = CertificateIssueResult(
                        status=CertificateIssueStatus.CREATED,
                        certificate_id=locked_certificate.pk,
                    )
        except (Certificate.DoesNotExist, DatabaseError):
            self.logger.exception(
                "Failed to attach certificate file certificate_id=%s user_id=%s course_id=%s",
                certificate.pk,
                user_id,
                course_id,
            )
            self._delete_stored_file(storage, stored_name)
            self._delete_unfinished_certificate(certificate.pk)
            return CertificateIssueResult(
                status=CertificateIssueStatus.FAILED,
                reason="database_error",
            )

        if result.status == CertificateIssueStatus.EXISTING:
            self._delete_stored_file(storage, stored_name)
        return result

    @staticmethod
    def _get_or_create_certificate(
        *,
        user_id: int,
        course_id: int,
        recipient_name: str,
        course_title: str,
        attempt_score: int,
        completed_at: date,
        expires_at: date,
    ) -> tuple[Certificate, bool]:
        defaults = {
            "recipient_name": recipient_name,
            "course_title": course_title,
            "result": attempt_score,
            "completed_at": completed_at,
            "expires_at": expires_at,
        }
        try:
            with transaction.atomic():
                return Certificate.objects.get_or_create(
                    user_id=user_id,
                    training_course_id=course_id,
                    defaults=defaults,
                )
        except IntegrityError:
            certificate = Certificate.objects.get(
                user_id=user_id,
                training_course_id=course_id,
            )
            return certificate, False

    @staticmethod
    def _read_template(template_file) -> bytes:
        template_file.open("rb")
        try:
            return template_file.read()
        finally:
            template_file.close()

    @staticmethod
    def _result_for_existing(certificate: Certificate) -> CertificateIssueResult:
        if certificate.certificate_file:
            return CertificateIssueResult(
                status=CertificateIssueStatus.EXISTING,
                certificate_id=certificate.pk,
            )
        return CertificateIssueResult(
            status=CertificateIssueStatus.PENDING,
            certificate_id=certificate.pk,
            reason="generation_in_progress",
        )

    def _delete_unfinished_certificate(self, certificate_id: int) -> None:
        try:
            Certificate.objects.filter(
                pk=certificate_id,
                certificate_file="",
            ).delete()
        except DatabaseError:
            self.logger.exception(
                "Failed to delete unfinished certificate certificate_id=%s",
                certificate_id,
            )

    def _delete_stored_file(self, storage, stored_name: str) -> None:
        try:
            storage.delete(stored_name)
        except Exception:
            self.logger.exception(
                "Failed to delete orphan certificate file name=%s",
                stored_name,
            )

    @staticmethod
    def _normalize_snapshot(value: str | None) -> str:
        return " ".join((value or "").split())

    @staticmethod
    def _validate_attempt_context(
        *,
        user_id: int,
        course_id: int,
        attempt_score: int,
        attempt_passed: bool,
        completed_at: date,
    ) -> None:
        if not isinstance(user_id, int) or isinstance(user_id, bool) or user_id < 1:
            raise CertificateIssuanceError("user_id должен быть положительным integer.")
        if (
            not isinstance(course_id, int)
            or isinstance(course_id, bool)
            or course_id < 1
        ):
            raise CertificateIssuanceError(
                "course_id должен быть положительным integer."
            )
        if (
            not isinstance(attempt_score, int)
            or isinstance(attempt_score, bool)
            or not 0 <= attempt_score <= 100
        ):
            raise CertificateIssuanceError(
                "attempt_score должен быть integer в диапазоне 0–100."
            )
        if not isinstance(attempt_passed, bool):
            raise CertificateIssuanceError("attempt_passed должен быть boolean.")
        if not isinstance(completed_at, date) or isinstance(completed_at, datetime):
            raise CertificateIssuanceError(
                "completed_at должен быть календарной датой без времени."
            )
