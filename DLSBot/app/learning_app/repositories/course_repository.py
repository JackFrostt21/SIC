# app/educational_module/repositories/course_repository.py
from typing import List, Optional, Dict, Any
from app.core.async_utils import AsyncRepository
from app.learning_app.models.courses import TrainingCourse
import logging


class CourseRepository(AsyncRepository[TrainingCourse]):
    """
    Репозиторий для работы с курсами.
    """

    def __init__(self):
        super().__init__(TrainingCourse)

    async def get_available_courses_for_user(
        self, user_id: int, is_actual: bool = True
    ) -> List[TrainingCourse]:
        """
        Получает список доступных курсов для пользователя с учетом групп и дедлайнов
        """
        # TODO: Реализовать полноценную логику с учетом user_id, групп и дедлайнов,
        # аналогично get_available_courses, но для внутреннего ID пользователя.
        # Пока что это заглушка, возвращающая все актуальные курсы.
        return await self.filter(is_actual=is_actual)

    async def get_available_courses(self, telegram_id: int) -> List[Dict[str, Any]]:
        """
        Получает список доступных курсов для пользователя Telegram с информацией о статусе теста.

        :param telegram_id: ID пользователя в Telegram
        :return: Список словарей, где каждый словарь содержит объект курса и статус теста.
        """
        logger = logging.getLogger(__name__)
        logger.info(
            f"Attempting to get available courses for telegram_id: {telegram_id}"
        )

        from app.bot.models import TelegramUser, UserTest
        from app.core.async_utils import AsyncUnitOfWork

        def _get_available_courses_with_test_status_sync():
            import datetime
            from django.db.models import (
                Q,
                OuterRef,
                Subquery,
                BooleanField,
                Case,
                When,
                Value,
            )

            courses_with_status = []
            try:
                user = TelegramUser.objects.get(user_id=telegram_id)
                user_groups = user.groups.all()
                today = datetime.date.today()
                logger.info(
                    f"User {telegram_id} found. Groups: {user_groups}. Today: {today}"
                )

                # Получаем базовый список курсов
                available_courses = TrainingCourse.objects.filter(is_actual=True)
                available_courses = available_courses.filter(
                    Q(user=user) | Q(group__in=user_groups)
                ).distinct()
                available_courses = available_courses.exclude(
                    Q(
                        deadlines__deadline_date__lte=today,
                        deadlines__deadline_users=user,
                    )
                    | Q(
                        deadlines__deadline_date__lte=today,
                        deadlines__deadline_groups__in=user_groups,
                    )
                ).order_by("title")

                logger.info(
                    f"Found {available_courses.count()} available courses for user {telegram_id} before checking test status."
                )

                # Для каждого курса получаем статус последнего теста
                for course in available_courses:
                    latest_test = (
                        UserTest.objects.filter(user=user, training=course)
                        .order_by("-created_at")
                        .first()
                    )

                    test_status = None
                    test_score = None
                    if latest_test:
                        test_status = (
                            "completed_passed"
                            if latest_test.complete
                            else "completed_failed"
                        )
                        test_score = latest_test.quantity_correct

                    courses_with_status.append(
                        {
                            "course": course,
                            "test_status": test_status,
                            "test_score": test_score,
                        }
                    )

                logger.info(
                    f"Finished processing courses for user {telegram_id}. Courses with status: {len(courses_with_status)}"
                )
                return courses_with_status
            except TelegramUser.DoesNotExist:
                logger.warning(
                    f"TelegramUser with user_id {telegram_id} does not exist."
                )
                return []
            except Exception as e:
                logger.error(
                    f"Error in _get_available_courses_with_test_status_sync for telegram_id {telegram_id}: {e}",
                    exc_info=True,
                )
                return []

        result = await AsyncUnitOfWork.execute(
            _get_available_courses_with_test_status_sync
        )
        logger.info(f"Result for telegram_id {telegram_id}: {result}")
        return result

    async def get_course_with_topics(
        self, course_id: int, user_id: Optional[int] = None
    ) -> Optional[dict]:
        """
        Получает курс вместе с его темами и статусом теста для указанного пользователя.
        """
        from app.core.async_utils import AsyncUnitOfWork
        from app.learning_app.models.courses import CourseTopic
        from app.bot.models import UserTest, TelegramUser

        def _get_course_and_test_status_sync():
            try:
                course = TrainingCourse.objects.get(id=course_id)
                topics_list = list(
                    CourseTopic.objects.filter(
                        training_course=course, is_actual=True
                    ).order_by("order")
                )

                test_status_val = None
                test_score_val = None

                if user_id:
                    try:
                        app_user = TelegramUser.objects.get(id=user_id)
                        latest_test = (
                            UserTest.objects.filter(user=app_user, training=course)
                            .order_by("-created_at")
                            .first()
                        )
                        if latest_test:
                            test_status_val = (
                                "completed_passed"
                                if latest_test.complete
                                else "completed_failed"
                            )
                            test_score_val = latest_test.quantity_correct
                    except TelegramUser.DoesNotExist:
                        pass  # Пользователь не найден, статус теста останется None

                return {
                    "course": course,
                    "topics": topics_list,
                    "test_status": test_status_val,
                    "test_score": test_score_val,
                }
            except TrainingCourse.DoesNotExist:
                return None

        return await AsyncUnitOfWork.execute(_get_course_and_test_status_sync)
