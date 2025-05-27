from typing import List, Optional
from app.core.async_utils import AsyncRepository, AsyncUnitOfWork
from app.learning_app.models.testing import TopicQuestion, AnswerOption
from app.learning_app.models.courses import TrainingCourse


class QuestionRepository(AsyncRepository[TopicQuestion]):
    """
    Репозиторий для работы с вопросами тестов.
    """

    def __init__(self):
        super().__init__(TopicQuestion)

    async def get_questions_for_course(
        self, course_id: int, prefetch_answers: bool = True
    ) -> List[TopicQuestion]:
        """
        Получает все актуальные вопросы для указанного курса, отсортированные по порядку.
        Опционально предзагружает варианты ответов.
        """

        def _get_questions_sync():
            qs = TopicQuestion.objects.filter(
                training_id=course_id, is_actual=True
            ).order_by("order")
            if prefetch_answers:
                # TODO: посмотерть, нужно ли это или мы сортируемся по полю order в модели AnswerOption
                qs = qs.prefetch_related("answer_options")
            return list(qs)

        questions = await AsyncUnitOfWork.execute(_get_questions_sync)
        # Если нужна явная сортировка ответов в Python:
        if prefetch_answers:
            for question in questions:
                # Сортируем варианты ответов по их полю 'order', если они были предзагружены
                if (
                    hasattr(question, "_prefetched_objects_cache")
                    and "answer_options" in question._prefetched_objects_cache
                ):
                    sorted_options = sorted(
                        list(question.answer_options.all()), key=lambda opt: opt.order
                    )
                    question.answer_options_sorted = (
                        sorted_options  # Сохраняем в новый атрибут
                    )
                else:  # Если prefetch не сработал как ожидалось или ответы не загрузились
                    options = await AnswerOptionRepository().get_answers_for_question(
                        question.id
                    )
                    question.answer_options_sorted = options
        return questions

    async def get_question_by_id(
        self, question_id: int, prefetch_answers: bool = True
    ) -> Optional[TopicQuestion]:
        """
        Получает вопрос по ID с вариантами ответов.
        """

        def _get_question_sync():
            try:
                q = TopicQuestion.objects.get(id=question_id, is_actual=True)
                return q
            except TopicQuestion.DoesNotExist:
                return None

        question = await AsyncUnitOfWork.execute(_get_question_sync)
        if question and prefetch_answers:
            # Явно загрузим и отсортируем ответы, т.к. prefetch_related в get() не так прост
            options = await AnswerOptionRepository().get_answers_for_question(
                question.id
            )
            question.answer_options_sorted = options
        return question


class AnswerOptionRepository(AsyncRepository[AnswerOption]):
    """
    Репозиторий для работы с вариантами ответов.
    """

    def __init__(self):
        super().__init__(AnswerOption)

    async def get_answers_for_question(self, question_id: int) -> List[AnswerOption]:
        """
        Получает все актуальные варианты ответов для указанного вопроса, отсортированные по порядку.
        """

        def _get_answers_sync():
            return list(
                AnswerOption.objects.filter(
                    topic_question_id=question_id, is_actual=True
                ).order_by("order")
            )

        return await AsyncUnitOfWork.execute(_get_answers_sync)
