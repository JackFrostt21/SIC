from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from app.learning_app.services.certificate_service import (
    CertificateIssueResult,
    CertificateIssueStatus,
)
from app.learning_app.services.test_service import TestService


class TestServiceCertificateIntegrationTests(SimpleTestCase):
    def setUp(self):
        self.test_service = TestService()
        self.test_service.certificate_service.aissue_for_course_attempt = AsyncMock(
            return_value=CertificateIssueResult(
                status=CertificateIssueStatus.CREATED,
                certificate_id=42,
            )
        )

    async def test_successful_course_attempt_issues_certificate(self):
        completed_at = date(2026, 8, 5)
        with patch(
            "app.learning_app.services.test_service.timezone.localdate",
            return_value=completed_at,
        ):
            result = await self.test_service._issue_certificate_for_attempt(
                user_id=10,
                course_id=20,
                attempt_score=95,
                attempt_passed=True,
                topic_id=None,
            )

        self.assertEqual(
            result,
            {"status": "created", "id": 42, "reason": None},
        )
        self.test_service.certificate_service.aissue_for_course_attempt.assert_awaited_once_with(
            user_id=10,
            course_id=20,
            attempt_score=95,
            attempt_passed=True,
            completed_at=completed_at,
        )

    async def test_submit_test_uses_current_backend_calculated_attempt(self):
        completed_at = date(2026, 8, 5)
        user = SimpleNamespace(id=10, company_id=7)
        course = SimpleNamespace(
            id=20,
            title="Охрана труда",
            min_test_percent_course=90,
        )
        answer = SimpleNamespace(id=101, is_correct=True)
        answer_options = Mock()
        answer_options.all.return_value = [answer]
        question = SimpleNamespace(
            id=100,
            is_multiple_choice=False,
            answer_options=answer_options,
        )
        self.test_service.user_repo.get_by_telegram_id = AsyncMock(
            return_value=user
        )
        self.test_service.course_repo.get_by_id = AsyncMock(return_value=course)
        self.test_service.question_repo.get_questions_for_course = AsyncMock(
            return_value=[question]
        )
        self.test_service.user_test_repo.get_best_user_test = AsyncMock(
            return_value=None
        )
        self.test_service.user_test_repo.update_or_create_user_test = AsyncMock()
        self.test_service.settings_repo.get_test_result_image_path = AsyncMock(
            return_value="test-passed.png"
        )

        with patch(
            "app.learning_app.services.test_service.timezone.localdate",
            return_value=completed_at,
        ):
            result = await self.test_service.submit_test(
                telegram_id=777,
                course_id=course.id,
                user_answers={question.id: [answer.id]},
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["score_percentage"], 100)
        self.assertTrue(result["passed"])
        self.assertEqual(
            result["certificate"],
            {"status": "created", "id": 42, "reason": None},
        )
        self.test_service.certificate_service.aissue_for_course_attempt.assert_awaited_once_with(
            user_id=user.id,
            course_id=course.id,
            attempt_score=100,
            attempt_passed=True,
            completed_at=completed_at,
        )

    async def test_successful_web_course_attempt_issues_certificate(self):
        completed_at = date(2026, 8, 6)
        user = SimpleNamespace(id=10)
        course = SimpleNamespace(
            id=20,
            title="Охрана труда",
            min_test_percent_course=90,
        )
        self._configure_web_repositories(user=user, course=course)

        with patch(
            "app.learning_app.services.test_service.timezone.localdate",
            return_value=completed_at,
        ):
            result = await self.test_service.submit_test_from_web(
                user_id=user.id,
                course_id=course.id,
                quantity_correct=95,
            )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["certificate"],
            {"status": "created", "id": 42, "reason": None},
        )
        self.test_service.certificate_service.aissue_for_course_attempt.assert_awaited_once_with(
            user_id=user.id,
            course_id=course.id,
            attempt_score=95,
            attempt_passed=True,
            completed_at=completed_at,
        )

    async def test_failed_web_attempt_does_not_use_historical_pass_for_certificate(self):
        user = SimpleNamespace(id=10)
        course = SimpleNamespace(
            id=20,
            title="Охрана труда",
            min_test_percent_course=90,
        )
        best_previous_test = SimpleNamespace(
            quantity_correct=95,
            complete=True,
        )
        self._configure_web_repositories(
            user=user,
            course=course,
            best_previous_test=best_previous_test,
        )

        result = await self.test_service.submit_test_from_web(
            user_id=user.id,
            course_id=course.id,
            quantity_correct=50,
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 95)
        self.assertIsNone(result["certificate"])
        self.test_service.certificate_service.aissue_for_course_attempt.assert_not_awaited()

    async def test_successful_web_topic_attempt_does_not_issue_certificate(self):
        user = SimpleNamespace(id=10)
        course = SimpleNamespace(
            id=20,
            title="Охрана труда",
            min_test_percent_course=90,
        )
        topic = SimpleNamespace(
            id=30,
            title="Первая помощь",
            training_course_id=course.id,
        )
        self._configure_web_repositories(user=user, course=course)
        self.test_service.topic_repo.get_by_id = AsyncMock(return_value=topic)

        result = await self.test_service.submit_test_from_web(
            user_id=user.id,
            course_id=course.id,
            topic_id=topic.id,
            quantity_correct=100,
        )

        self.assertTrue(result["success"])
        self.assertIsNone(result["certificate"])
        self.test_service.certificate_service.aissue_for_course_attempt.assert_not_awaited()

    async def test_web_certificate_error_does_not_break_test_result(self):
        user = SimpleNamespace(id=10)
        course = SimpleNamespace(
            id=20,
            title="Охрана труда",
            min_test_percent_course=90,
        )
        self._configure_web_repositories(user=user, course=course)
        self.test_service.certificate_service.aissue_for_course_attempt.side_effect = (
            RuntimeError("unexpected")
        )

        with self.assertLogs(
            "app.learning_app.services.test_service",
            level="ERROR",
        ):
            result = await self.test_service.submit_test_from_web(
                user_id=user.id,
                course_id=course.id,
                quantity_correct=95,
            )

        self.assertTrue(result["success"])
        self.assertEqual(
            result["certificate"],
            {"status": "failed", "id": None, "reason": "unexpected_error"},
        )

    def test_web_endpoint_exposes_certificate_result(self):
        user = SimpleNamespace(id=10)
        course = SimpleNamespace(id=20, archive=False)
        service = Mock()
        service.submit_test_from_web = AsyncMock(
            return_value={
                "success": True,
                "score": 95,
                "passed": True,
                "message": "Тест пройден",
                "course_title": "Охрана труда",
                "topic_title": None,
                "certificate": {
                    "status": "created",
                    "id": 42,
                    "reason": None,
                },
            }
        )

        with (
            patch(
                "app.bot.views.test_views.TelegramUser.objects.get",
                return_value=user,
            ),
            patch(
                "app.bot.views.test_views.TrainingCourse.objects.get",
                return_value=course,
            ),
            patch(
                "app.bot.views.test_views.TestService",
                return_value=service,
            ),
        ):
            client = APIClient()
            client.force_authenticate(
                user=SimpleNamespace(pk=999, is_authenticated=True),
            )
            response = client.post(
                reverse("course_test_submit", kwargs={"course_id": course.id}),
                {
                    "user_id": user.id,
                    "course_id": course.id,
                    "quantity_correct": 95,
                },
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["certificate"],
            {"status": "created", "id": 42, "reason": None},
        )
        service.submit_test_from_web.assert_awaited_once_with(
            user_id=user.id,
            course_id=course.id,
            topic_id=None,
            quantity_correct=95,
        )

    async def test_failed_current_attempt_does_not_issue_certificate(self):
        result = await self.test_service._issue_certificate_for_attempt(
            user_id=10,
            course_id=20,
            attempt_score=89,
            attempt_passed=False,
            topic_id=None,
        )

        self.assertIsNone(result)
        self.test_service.certificate_service.aissue_for_course_attempt.assert_not_awaited()

    async def test_topic_attempt_does_not_issue_certificate(self):
        result = await self.test_service._issue_certificate_for_attempt(
            user_id=10,
            course_id=20,
            attempt_score=100,
            attempt_passed=True,
            topic_id=30,
        )

        self.assertIsNone(result)
        self.test_service.certificate_service.aissue_for_course_attempt.assert_not_awaited()

    async def test_unexpected_issue_error_does_not_break_test_result(self):
        self.test_service.certificate_service.aissue_for_course_attempt.side_effect = (
            RuntimeError("unexpected")
        )

        with self.assertLogs(
            "app.learning_app.services.test_service",
            level="ERROR",
        ):
            result = await self.test_service._issue_certificate_for_attempt(
                user_id=10,
                course_id=20,
                attempt_score=95,
                attempt_passed=True,
                topic_id=None,
            )

        self.assertEqual(
            result,
            {"status": "failed", "id": None, "reason": "unexpected_error"},
        )

    def _configure_web_repositories(
        self,
        *,
        user,
        course,
        best_previous_test=None,
    ):
        self.test_service.user_repo.get_by_id = AsyncMock(return_value=user)
        self.test_service.course_repo.get_by_id = AsyncMock(return_value=course)
        self.test_service.user_test_repo.get_best_user_test = AsyncMock(
            return_value=best_previous_test
        )
        self.test_service.user_test_repo.update_or_create_user_test = AsyncMock()
