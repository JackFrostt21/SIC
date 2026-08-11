from typing import List, Optional, Dict, Any
from app.core.async_utils import AsyncRepository, AsyncUnitOfWork
from app.bot.models import UserTest
from app.learning_app.models.courses import TrainingCourse, CourseTopic
from app.learning_app.models.testing import TopicQuestion, AnswerOption


class UserTestRepository(AsyncRepository[UserTest]):
    """
    Репозиторий для работы с результатами тестирования пользователей.
    Предоставляет асинхронные методы для операций с моделью UserTest.
    """

    def __init__(self):
        super().__init__(UserTest)

    @staticmethod
    def _build_scope_filter(
        course_id: Optional[int], topic_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Отдаёт фильтр, приоритет за topic_id: если задан topic_id, используем его,
        иначе используем course_id. Если оба None — ошибка.
        """
        if topic_id:
            return {"course_topic_id": topic_id}
        if course_id:
            return {"training_id": course_id}
        raise ValueError("Нужно передать course_id или topic_id.")

    async def get_test_result(
        self,
        user_id: int,
        course_id: Optional[int] = None,
        topic_id: Optional[int] = None,
    ) -> Optional[UserTest]:
        """
        Получает результат теста пользователя по курсу.

        :param user_id: ID пользователя
        :param course_id: ID курса
        :return: Объект с результатами теста или None, если тест не найден
        """
        scope_filter = self._build_scope_filter(course_id, topic_id)
        return await self.get_by_filter(user_id=user_id, **scope_filter)

    async def create_empty_test(
        self,
        user_id: int,
        course_id: Optional[int] = None,
        topic_id: Optional[int] = None,
    ) -> UserTest:
        """
        Создает пустой тест для пользователя.

        :param user_id: ID пользователя
        :param course_id: ID курса
        :return: Созданный объект теста
        """
        scope_filter = self._build_scope_filter(course_id, topic_id)
        return await self.create(
            user_id=user_id,
            **scope_filter,
            user_answer={"results": []},
            complete=False,
        )

    async def get_or_create_test(
        self,
        user_id: int,
        course_id: Optional[int] = None,
        topic_id: Optional[int] = None,
    ) -> UserTest:
        """
        Получает существующий или создает новый тест для пользователя.

        :param user_id: ID пользователя
        :param course_id: ID курса
        :return: Объект теста
        """
        test = await self.get_test_result(user_id, course_id, topic_id)
        if not test:
            return await self.create_empty_test(user_id, course_id, topic_id)
        return test

    async def save_answer(
        self,
        user_id: int,
        course_id: Optional[int],
        topic_id: Optional[int],
        question_id: int,
        answer_ids: List[str],
        is_multiple_choice: bool,
    ) -> UserTest:
        """
        Сохраняет ответ пользователя на вопрос теста.

        :param user_id: ID пользователя
        :param course_id: ID курса
        :param topic_id: ID темы (если тест по теме)
        :param question_id: ID вопроса
        :param answer_ids: Список ID выбранных ответов
        :param is_multiple_choice: Флаг множественного выбора
        :return: Обновленный объект теста
        """

        def _save_answer():
            scope_filter = self._build_scope_filter(course_id, topic_id)
            # Получаем или создаем запись теста
            user_test, _ = UserTest.objects.get_or_create(
                user_id=user_id,
                **scope_filter,
                defaults={"user_answer": {"results": []}},
            )

            # Получаем текущие ответы
            current_user_answer = user_test.user_answer

            # Получаем все правильные ответы для вопроса
            correct_answers = list(
                AnswerOption.objects.filter(
                    topic_question_id=question_id, is_correct=True
                ).values_list("id", flat=True)
            )
            correct_answers = list(map(str, correct_answers))

            # Проверяем, есть ли уже ответ на этот вопрос
            existing_result = next(
                (
                    result
                    for result in current_user_answer["results"]
                    if result["question_id"] == str(question_id)
                ),
                None,
            )

            # Определяем, правильный ли ответ
            is_correct = set(answer_ids) == set(correct_answers)

            if existing_result:
                # Обновляем существующий ответ
                existing_result["answer_id"] = answer_ids
                existing_result["is_correct"] = is_correct
            else:
                # Добавляем новый ответ
                new_result = {
                    "question_id": str(question_id),
                    "answer_id": answer_ids,
                    "is_correct": is_correct,
                }
                current_user_answer["results"].append(new_result)

            # Сохраняем обновленные ответы
            user_test.user_answer = current_user_answer
            user_test.save(update_fields=["user_answer"])

            return user_test

        return await AsyncUnitOfWork.execute(_save_answer)

    async def count_results(
        self,
        user_id: int,
        course_id: Optional[int] = None,
        topic_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Подсчитывает результаты теста.

        :param user_id: ID пользователя
        :param course_id: ID курса
        :return: Словарь с результатами теста
        """

        def _count_results():
            scope_filter = self._build_scope_filter(course_id, topic_id)
            try:
                user_test = UserTest.objects.get(user_id=user_id, **scope_filter)
            except UserTest.DoesNotExist:
                training_course = None
                topic = None
                if course_id:
                    training_course = TrainingCourse.objects.filter(id=course_id).first()
                if topic_id and not training_course:
                    topic = CourseTopic.objects.filter(id=topic_id).select_related(
                        "training_course"
                    ).first()
                    training_course = topic.training_course if topic else None
                min_percent = (
                    training_course.min_test_percent_course if training_course else 0
                )
                return {
                    "correct_count": 0,
                    "incorrect_count": 0,
                    "total_count": 0,
                    "correct_percent": 0,
                    "incorrect_percent": 0,
                    "is_complete": False,
                    "min_percent_required": min_percent,
                    "course_title": (
                        training_course.title
                        if training_course
                        else (topic.title if topic else "")
                    ),
                }

            result_test = user_test.user_answer
            correct_count = sum(1 for i in result_test["results"] if i["is_correct"])
            incorrect_count = len(result_test["results"]) - correct_count

            total_count = correct_count + incorrect_count
            if total_count == 0:
                correct_percent = 0
                incorrect_percent = 0
            else:
                correct_percent = 100 * correct_count // total_count
                incorrect_percent = 100 * incorrect_count // total_count

            training_course = None
            topic = None
            if course_id:
                training_course = TrainingCourse.objects.filter(id=course_id).first()
            if topic_id and not training_course:
                topic = CourseTopic.objects.filter(id=topic_id).select_related(
                    "training_course"
                ).first()
                training_course = topic.training_course if topic else None

            min_percent_required = (
                training_course.min_test_percent_course if training_course else 0
            )
            is_complete = correct_percent >= min_percent_required

            # Обновляем запись только если результат лучше предыдущего
            if (
                user_test.quantity_correct is None
                or correct_percent > user_test.quantity_correct
            ):
                user_test.complete = is_complete
                user_test.quantity_correct = correct_percent
                user_test.quantity_not_correct = incorrect_percent
                user_test.save()

            return {
                "correct_count": correct_count,
                "incorrect_count": incorrect_count,
                "total_count": total_count,
                "correct_percent": correct_percent,
                "incorrect_percent": incorrect_percent,
                "is_complete": is_complete,
                "min_percent_required": min_percent_required,
                "course_title": (
                    training_course.title
                    if training_course
                    else (topic.title if topic else "")
                ),
            }

        return await AsyncUnitOfWork.execute(_count_results)

    async def get_selected_answers(
        self,
        user_id: int,
        course_id: Optional[int],
        topic_id: Optional[int],
        question_id: int,
    ) -> List[str]:
        """
        Получает ранее выбранные ответы пользователя на вопрос.

        :param user_id: ID пользователя
        :param course_id: ID курса
        :param question_id: ID вопроса
        :return: Список ID выбранных ответов
        """

        def _get_selected_answers():
            scope_filter = self._build_scope_filter(course_id, topic_id)
            try:
                user_test = UserTest.objects.get(user_id=user_id, **scope_filter)

                # Ищем ответ на конкретный вопрос
                for result in user_test.user_answer["results"]:
                    if result["question_id"] == str(question_id):
                        return result["answer_id"]

                return []
            except UserTest.DoesNotExist:
                return []

        return await AsyncUnitOfWork.execute(_get_selected_answers)

    async def get_completed_courses(self, user_id: int) -> List[int]:
        """
        Получает список ID курсов, по которым пользователь успешно прошел тестирование.

        :param user_id: ID пользователя
        :return: Список ID успешно пройденных курсов
        """

        def _get_completed_courses():
            completed_tests = UserTest.objects.filter(user_id=user_id, complete=True)
            return [test.training_id for test in completed_tests]

        return await AsyncUnitOfWork.execute(_get_completed_courses)

    async def update_or_create_user_test(
        self,
        user_id: int,
        score: int,
        is_complete: bool,
        course_id: Optional[int] = None,
        topic_id: Optional[int] = None,
    ) -> UserTest:
        """
        Обновляет существующую запись UserTest или создает новую с предоставленными результатами.
        Не выполняет логику "лучшего результата", просто сохраняет переданные данные.

        :param user_id: ID пользователя.
        :param course_id: ID курса (в модели это training_id).
        :param score: Финальный процент правильных ответов (сохраняется в quantity_correct).
        :param is_complete: True, если тест пройден.
        :return: Сохраненный или созданный объект UserTest.
        """

        def _update_or_create():
            scope_filter = self._build_scope_filter(course_id, topic_id)
            user_test, created = UserTest.objects.get_or_create(
                user_id=user_id,
                defaults={
                    "quantity_correct": score,
                    "complete": is_complete,
                    **scope_filter,
                },
                **scope_filter,
            )
            if not created:
                user_test.quantity_correct = score
                user_test.complete = is_complete
                user_test.save(update_fields=["quantity_correct", "complete"])
            return user_test

        return await AsyncUnitOfWork.execute(_update_or_create)

    async def get_best_user_test(
        self, user_id: int, course_id: Optional[int] = None, topic_id: Optional[int] = None
    ) -> Optional[UserTest]:
        """
        Получает лучший (или единственный) результат теста пользователя по курсу.
        В текущей логике TestService сам определяет, какой результат "лучший"
        перед сохранением, поэтому этот метод просто возвращает существующую запись,
        если она есть, т.к. она уже должна быть "лучшей".

        :param user_id: ID пользователя
        :param course_id: ID курса
        :param topic_id: ID темы
        :return: Объект UserTest или None
        """
        scope_filter = self._build_scope_filter(course_id, topic_id)
        return await self.get_by_filter(user_id=user_id, **scope_filter)
