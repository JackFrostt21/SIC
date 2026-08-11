from typing import Dict, Any, Optional, List, Tuple
import random
import logging

from django.utils import timezone

from app.learning_app.repositories.course_repository import CourseRepository
from app.learning_app.repositories.question_repository import QuestionRepository
from app.learning_app.repositories.topic_repository import TopicRepository
from app.bot.repositories.telegram_user_repository import TelegramUserRepository
from app.bot.repositories.user_test_repository import UserTestRepository
from app.organization.repositories.company_repository import SettingsBotRepository
from app.learning_app.models.courses import TrainingCourse
from app.learning_app.models.testing import TopicQuestion, AnswerOption
from app.bot.models.telegram_user import TelegramUser
from app.bot.models import UserTest
from app.learning_app.services.certificate_service import CertificateService


class TestService:
    """
    Сервис для управления процессом тестирования.
    """

    def __init__(self):
        self.course_repo = CourseRepository()
        self.question_repo = QuestionRepository()
        self.topic_repo = TopicRepository()
        self.user_repo = TelegramUserRepository()
        self.user_test_repo = UserTestRepository()
        self.settings_repo = SettingsBotRepository()
        self.certificate_service = CertificateService()
        self.logger = logging.getLogger(__name__)

    async def start_test_attempt(
        self,
        telegram_id: int,
        course_id: Optional[int] = None,
        topic_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Начинает новую попытку тестирования для пользователя по курсу.
        Возвращает первый вопрос или информацию об ошибке.
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return {"success": False, "message": "Пользователь не найден."}

        if not course_id and not topic_id:
            return {"success": False, "message": "Не указан курс или тема."}

        course_info = None
        topic_info = None
        if topic_id:
            topic_info = await self.topic_repo.get_by_id(topic_id)
            if not topic_info:
                return {"success": False, "message": "Тема не найдена."}
            course_id = topic_info.training_course_id
            course_info = await self.course_repo.get_by_id(course_id)
        else:
            course_info = await self.course_repo.get_by_id(course_id)
            if not course_info:
                return {"success": False, "message": "Курс не найден."}

        questions = await self.question_repo.get_questions_for_course(
            course_id=course_id if not topic_id else None,
            topic_id=topic_id,
            prefetch_answers=True,
        )
        try:
            q_count = len(questions)
        except Exception:
            q_count = 0
        # Логируем в stdout, чтобы точно увидеть даже без настроек логгера
        print(f"[TEST START SERVICE] course_id={course_id} topic_id={topic_id} questions_found={q_count}")
        if not questions:
            scope_label = f"раздела «{topic_info.title}»" if topic_info else "курса"
            return {
                "success": False,
                "message": f"Для {scope_label} нет теста.",
            }

        # TODO: ПРОТЕСТИРОВАТЬ НОВУЮ ЛОГИКУ, отказался от очистки UserTest перед тестированием, так как поменял логику сохранения результат, сейчас ТОЛЬКО лучший результат:
        # В этой версии мы не сохраняем UserTest до завершения.

        # Возвращаем первый вопрос
        current_question_index = 0
        question_data = self._format_question_data(
            questions[current_question_index], current_question_index, len(questions)
        )

        return {
            "success": True,
            "course_title": course_info.title if course_info else None,
            "topic_title": topic_info.title if topic_info else None,
            "total_questions": len(questions),
            "current_question_index": current_question_index,
            "question": question_data,
            "all_questions_ids": [
                q.id for q in questions
            ],  # Передаем ID всех вопросов для навигации
            # TODO: переделать, чтобы ответы хранились в FSM
            # "user_answers": {} # Здесь будем хранить ответы пользователя в сессии/FSM
        }

    def _format_question_data(
        self, question: TopicQuestion, index: int, total: int
    ) -> Dict[str, Any]:
        """
        Форматирует данные вопроса для отображения.
        """
        options = []
        # Используем answer_options_sorted, если он был предзагружен и отсортирован в репозитории
        answer_options_list = getattr(
            question, "answer_options_sorted", question.answer_options.all()
        )

        for option in answer_options_list:
            options.append(
                {"id": option.id, "text": option.text, "order": option.order}
            )

        return {
            "id": question.id,
            "text": question.title,
            "is_multiple_choice": question.is_multiple_choice,
            "order": index + 1,  # 1-based index for display
            "total_in_test": total,
            "options": options,
        }

    async def get_next_question_data(
        self,
        course_id: int,
        all_questions_ids: List[int],
        current_question_index: int,
        # user_answers: Dict[int, List[int]] # Ответы пользователя
    ) -> Dict[str, Any]:
        """
        Получает данные для следующего вопроса.
        """
        next_question_index = current_question_index + 1
        try:
            print(
                f"[TEST SERVICE NEXT] current_idx={current_question_index} next_idx={next_question_index} total={len(all_questions_ids)}"
            )
        except Exception:
            pass
        if next_question_index >= len(all_questions_ids):
            return {
                "success": False,
                "message": "Это был последний вопрос.",
                "is_last": True,
            }

        question_id = all_questions_ids[next_question_index]
        try:
            print(f"[TEST SERVICE NEXT] fetching q_id={question_id}")
        except Exception:
            pass
        question = await self.question_repo.get_question_by_id(
            question_id, prefetch_answers=True
        )
        if not question:
            return {"success": False, "message": "Ошибка: Следующий вопрос не найден."}

        question_data = self._format_question_data(
            question, next_question_index, len(all_questions_ids)
        )
        return {
            "success": True,
            "current_question_index": next_question_index,
            "question": question_data,
            "is_last": next_question_index == len(all_questions_ids) - 1,
        }

    async def get_prev_question_data(
        self,
        course_id: int,
        all_questions_ids: List[int],
        current_question_index: int,
    ) -> Dict[str, Any]:
        """
        Получает данные для предыдущего вопроса.
        """
        prev_question_index = current_question_index - 1
        try:
            print(
                f"[TEST SERVICE PREV] current_idx={current_question_index} prev_idx={prev_question_index}"
            )
        except Exception:
            pass
        if prev_question_index < 0:
            return {
                "success": False,
                "message": "Это был первый вопрос.",
                "is_first": True,
            }

        question_id = all_questions_ids[prev_question_index]
        try:
            print(f"[TEST SERVICE PREV] fetching q_id={question_id}")
        except Exception:
            pass
        question = await self.question_repo.get_question_by_id(
            question_id, prefetch_answers=True
        )
        if not question:
            return {"success": False, "message": "Ошибка: Предыдущий вопрос не найден."}

        question_data = self._format_question_data(
            question, prev_question_index, len(all_questions_ids)
        )
        return {
            "success": True,
            "current_question_index": prev_question_index,
            "question": question_data,
            "is_first": prev_question_index == 0,
        }

    async def submit_test(
        self,
        telegram_id: int,
        course_id: Optional[int],
        user_answers: Dict[int, List[int]],
        topic_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Обрабатывает ответы пользователя, подсчитывает результат и сохраняет его,
        если он лучше предыдущего.

        user_answers: Словарь, где ключ - ID вопроса, значение - список ID выбранных ответов.
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return {"success": False, "message": "Пользователь не найден."}

        if not course_id and not topic_id:
            return {"success": False, "message": "Не указан курс или тема."}

        topic = None
        course = None
        if topic_id:
            topic = await self.topic_repo.get_by_id(topic_id)
            if not topic:
                return {"success": False, "message": "Тема не найдена."}
            course_id = topic.training_course_id
            course = await self.course_repo.get_by_id(course_id)
        else:
            course = await self.course_repo.get_by_id(course_id)
            if not course:
                return {"success": False, "message": "Курс не найден."}

        questions_in_db = await self.question_repo.get_questions_for_course(
            course_id=course_id if not topic_id else None,
            topic_id=topic_id,
            prefetch_answers=True,
        )
        try:
            print(
                f"[TEST SUBMIT SERVICE] course_id={course_id} topic_id={topic_id} questions_found={len(questions_in_db)} ids={[q.id for q in questions_in_db]}"
            )
        except Exception:
            pass
        if not questions_in_db:
            return {"success": False, "message": "Вопросы для теста не найдены."}

        total_questions_count = len(questions_in_db)
        correct_answers_count = 0

        for question_db in questions_in_db:
            user_selected_answer_ids = set(user_answers.get(question_db.id, []))
            correct_option_ids = {
                opt.id for opt in question_db.answer_options.all() if opt.is_correct
            }

            if not correct_option_ids:
                continue

            if question_db.is_multiple_choice:
                if user_selected_answer_ids == correct_option_ids:
                    correct_answers_count += 1
            else:
                if (
                    len(correct_option_ids) == 1
                    and len(user_selected_answer_ids) == 1
                    and user_selected_answer_ids == correct_option_ids
                ):
                    correct_answers_count += 1

        score_percentage = 0
        if total_questions_count > 0:
            score_percentage = round(
                (correct_answers_count / total_questions_count) * 100
            )

        passed = score_percentage >= (course.min_test_percent_course or 90) if course else False

        # Получаем лучший предыдущий результат
        best_previous_test = await self.user_test_repo.get_best_user_test(
            user_id=user.id, course_id=course_id, topic_id=topic_id
        )

        should_save_current = True
        current_test_data_to_save = {
            "user_id": user.id,
            "course_id": course_id if not topic_id else None,
            "topic_id": topic_id,
            "score": score_percentage,
            "is_complete": passed,
        }

        if best_previous_test:
            prev_score = best_previous_test.quantity_correct
            prev_complete = best_previous_test.complete
            # Защита от None: если ранее не было сохранённого процента
            if prev_score is None:
                prev_score = 0
            if passed:
                if not prev_complete:
                    should_save_current = True
                else:
                    if score_percentage <= prev_score:
                        should_save_current = False
            else:
                if prev_complete:
                    should_save_current = False
                else:
                    if score_percentage <= prev_score:
                        should_save_current = False

        final_score_percentage = score_percentage
        final_passed_status = passed
        final_correct_answers = correct_answers_count

        if should_save_current:
            await self.user_test_repo.update_or_create_user_test(
                **current_test_data_to_save
            )
        else:
            # Используем сохранённые значения, защищая от None
            stored_score = best_previous_test.quantity_correct
            stored_complete = best_previous_test.complete
            if stored_score is None:
                stored_score = 0
            final_score_percentage = stored_score
            final_passed_status = stored_complete
            final_correct_answers = int(
                round(stored_score * total_questions_count / 100)
            )

        certificate_result = await self._issue_certificate_for_attempt(
            user_id=user.id,
            course_id=course.id,
            attempt_score=score_percentage,
            attempt_passed=passed,
            topic_id=topic_id,
        )

        # Получаем картинку для результата
        company_id_for_settings = (
            user.company_id if hasattr(user, "company_id") else None
        )
        image_path = await self.settings_repo.get_test_result_image_path(
            passed=final_passed_status, company_id=company_id_for_settings
        )

        return {
            "success": True,
            "course_title": course.title if course else (topic.title if topic else None),
            "topic_title": topic.title if topic else None,
            "score_percentage": final_score_percentage,
            "correct_answers_count": final_correct_answers,
            "total_questions_count": total_questions_count,
            "passed": final_passed_status,
            "min_test_percent_course": course.min_test_percent_course if course else None,
            "image_path": image_path,
            "certificate": certificate_result,
        }

    async def _issue_certificate_for_attempt(
        self,
        *,
        user_id: int,
        course_id: int,
        attempt_score: int,
        attempt_passed: bool,
        topic_id: Optional[int],
    ) -> Optional[Dict[str, Any]]:
        if topic_id or not attempt_passed:
            return None

        try:
            result = await self.certificate_service.aissue_for_course_attempt(
                user_id=user_id,
                course_id=course_id,
                attempt_score=attempt_score,
                attempt_passed=attempt_passed,
                completed_at=timezone.localdate(),
            )
        except Exception:
            self.logger.exception(
                "Unexpected certificate issue error user_id=%s course_id=%s",
                user_id,
                course_id,
            )
            return {
                "status": "failed",
                "id": None,
                "reason": "unexpected_error",
            }
        return result.as_dict()

    async def submit_test_from_web(
        self,
        user_id: int,
        course_id: Optional[int],
        quantity_correct: int,
        topic_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Упрощенная версия для веб-интерфейса.
        Принимает готовый результат (quantity_correct) и сохраняет его,
        если он лучше предыдущего, используя существующую логику.

        Временное ограничение MVP: user_id и quantity_correct поступают от
        клиента. До переноса расчёта результата и определения пользователя на
        backend этот путь нельзя считать защищённым от подмены.

        Args:
            user_id: ID пользователя из TelegramUser
            course_id: ID курса
            quantity_correct: Процент правильных ответов (0-100)

        Returns:
            Dict с результатом операции
        """
        # Получаем пользователя
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "Пользователь не найден."}

        if not course_id and not topic_id:
            return {"success": False, "message": "Не указан курс или тема."}

        course = None
        topic = None
        if topic_id:
            topic = await self.topic_repo.get_by_id(topic_id)
            if not topic:
                return {"success": False, "message": "Тема не найдена."}
            course_id = topic.training_course_id
            course = await self.course_repo.get_by_id(course_id)
        else:
            course = await self.course_repo.get_by_id(course_id)
            if not course:
                return {"success": False, "message": "Курс не найден."}

        # Вычисляем производные значения
        passed = quantity_correct >= (course.min_test_percent_course or 90)

        # Получаем лучший предыдущий результат (используем существующую логику)
        best_previous_test = await self.user_test_repo.get_best_user_test(
            user_id=user.id, course_id=course_id, topic_id=topic_id
        )

        should_save_current = True
        current_test_data_to_save = {
            "user_id": user.id,
            "course_id": course_id if not topic_id else None,
            "topic_id": topic_id,
            "score": quantity_correct,
            "is_complete": passed,
        }

        # Применяем существующую логику сравнения результатов
        if best_previous_test:
            if passed:  # Новый тест пройден
                if not best_previous_test.complete:
                    should_save_current = True  # Первый пройденный тест
                else:
                    if quantity_correct <= best_previous_test.quantity_correct:
                        should_save_current = False  # Новый результат хуже
            else:  # Новый тест НЕ пройден
                if best_previous_test.complete:
                    should_save_current = False  # Есть пройденный, не перезаписываем
                else:
                    if quantity_correct <= best_previous_test.quantity_correct:
                        should_save_current = (
                            False  # Новый результат хуже среди непройденных
                        )

        # Определяем финальные значения для ответа
        if should_save_current:
            # Сохраняем новый результат
            await self.user_test_repo.update_or_create_user_test(
                **current_test_data_to_save
            )
            final_score = quantity_correct
            final_passed = passed
        else:
            # Возвращаем существующий лучший результат
            final_score = best_previous_test.quantity_correct
            final_passed = best_previous_test.complete

        certificate_result = await self._issue_certificate_for_attempt(
            user_id=user.id,
            course_id=course.id,
            attempt_score=quantity_correct,
            attempt_passed=passed,
            topic_id=topic_id,
        )

        # Формируем сообщение
        message = f'Тест {"пройден" if final_passed else "не пройден"}. Результат: {final_score}% (минимум: {course.min_test_percent_course}%)'

        return {
            "success": True,
            "score": final_score,
            "passed": final_passed,
            "message": message,
            "course_title": course.title if course else (topic.title if topic else None),
            "topic_title": topic.title if topic else None,
            "certificate": certificate_result,
        }
