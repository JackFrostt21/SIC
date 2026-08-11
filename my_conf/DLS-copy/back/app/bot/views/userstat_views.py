from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.db.models import Q, Count

from ...learning_app.models import TrainingCourse, CourseTopic
from ...bot.models.telegram_user import TelegramUser
from ...bot.models.education_data import UserRead, UserTest
from ...bot.serializers.userstat_serializers import UserOverallStatSerializer
from ...bot.models.rating import UserRating


class UserStatsViewSet(viewsets.ViewSet):
    """
    Возвращает общую и детальную статистику прогресса пользователя.
    """

    @extend_schema(
        summary="Статистика пользователя",
        description="Общая и детальная статистика по курсам, темам и тестам для указанного TelegramUser",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID пользователя Telegram",
            )
        ],
        responses={200: UserOverallStatSerializer},
        tags=["Статистика пользователя"],
    )
    @action(detail=False, methods=["get"], url_path="user/(?P<user_id>[^/.]+)")
    def stats(self, request, user_id=None):
        try:
            user = TelegramUser.objects.get(pk=user_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_groups = user.groups.all()
        courses = TrainingCourse.objects.filter(
            Q(user=user) | Q(group__in=user_groups),
            archive=False,
            is_actual=True,
        ).distinct()

        courses_details = []
        total_topics_count = 0
        read_topics_count = 0
        passed_tests_count = 0

        for course in courses:
            topics = CourseTopic.objects.filter(training_course=course)
            course_total_topics = topics.count()
            course_read_topics = UserRead.objects.filter(
                user=user, is_read=True, topic__in=topics
            ).count()

            reading_progress = (
                (course_read_topics / course_total_topics * 100)
                if course_total_topics > 0
                else 0
            )

            test_passed = UserTest.objects.filter(
                user=user, training=course, complete=True
            ).exists()

            test_attempted = UserTest.objects.filter(
                user=user, training=course
            ).exists()

            if test_passed:
                test_status = "passed"
                passed_tests_count += 1
            elif test_attempted:
                test_status = "failed"
            else:
                test_status = "not_started"

            is_completed = reading_progress == 100 and test_passed

            courses_details.append(
                {
                    "course_id": course.id,
                    "course_title": course.title,
                    "total_topics": course_total_topics,
                    "read_topics": course_read_topics,
                    "reading_progress_percent": round(reading_progress, 2),
                    "test_status": test_status,
                    "is_completed": is_completed,
                }
            )

            total_topics_count += course_total_topics
            read_topics_count += course_read_topics

        total_courses = courses.count()
        total_tests = total_courses
        failed_tests = total_tests - passed_tests_count
        completed_courses = sum(1 for d in courses_details if d["is_completed"])

        overall_progress_topics = (
            (read_topics_count / total_topics_count * 100)
            if total_topics_count > 0
            else 0
        )

        overall_progress = (
            (completed_courses / total_courses * 100) if total_courses > 0 else 0
        )

        # Рейтинговые данные: points и place из UserRating
        rating_points = (
            UserRating.objects.filter(user=user)
            .values_list("points", flat=True)
            .first()
            or 0
        )
        rating_place = 1 + UserRating.objects.filter(points__gt=rating_points).count()

        summary_data = {
            "total_courses": total_courses,
            "completed_courses": completed_courses,
            "total_topics": total_topics_count,
            "read_topics": read_topics_count,
            "overall_progress_topics": round(overall_progress_topics, 2),
            "total_tests": total_tests,
            "passed_tests": passed_tests_count,
            "failed_tests": failed_tests,
            "overall_progress": round(overall_progress, 2),
            "place": rating_place,
            "points": rating_points,
        }

        response_data = {
            "summary": summary_data,
            "courses_details": courses_details,
        }

        serializer = UserOverallStatSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
