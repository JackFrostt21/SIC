from typing import Dict, Any, Optional, List, Tuple
import random

from app.learning_app.repositories.course_repository import CourseRepository
from app.learning_app.repositories.question_repository import QuestionRepository
from app.bot.repositories.telegram_user_repository import TelegramUserRepository
from app.bot.repositories.user_test_repository import UserTestRepository
from app.organization.repositories.company_repository import SettingsBotRepository
from app.learning_app.models.courses import TrainingCourse
from app.learning_app.models.testing import TopicQuestion, AnswerOption
from app.bot.models.telegram_user import TelegramUser
from app.bot.models import UserTest


class TestService:
    """
    Сервис для управления процессом тестирования.
    """

    def __init__(self):
        self.course_repo = CourseRepository()
        self.question_repo = QuestionRepository()
        self.user_repo = TelegramUserRepository()
        self.user_test_repo = UserTestRepository()
        self.settings_repo = SettingsBotRepository()

    async def start_test_attempt(
        self, telegram_id: int, course_id: int
    ) -> Dict[str, Any]:
        """
        Начинает новую попытку тестирования для пользователя по курсу.
        Возвращает первый вопрос или информацию об ошибке.
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return {"success": False, "message": "Пользователь не найден."}

        course_info = await self.course_repo.get_by_id(
            course_id
        )  # Используем базовый get_by_id
        if not course_info:
            return {"success": False, "message": "Курс не найден."}

        # course = course_info # course_info это уже объект TrainingCourse

        questions = await self.question_repo.get_questions_for_course(
            course_id, prefetch_answers=True
        )
        if not questions:
            return {"success": False, "message": "Для данного курса нет вопросов."}

        # TODO: ПРОТЕСТИРОВАТЬ НОВУЮ ЛОГИКУ, отказался от очистки UserTest перед тестированием, так как поменял логику сохранения результат, сейчас ТОЛЬКО лучший результат:
        # В этой версии мы не сохраняем UserTest до завершения.


        # Возвращаем первый вопрос
        current_question_index = 0
        question_data = self._format_question_data(
            questions[current_question_index], current_question_index, len(questions)
        )

        return {
            "success": True,
            "course_title": course_info.title,
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
        if next_question_index >= len(all_questions_ids):
            return {
                "success": False,
                "message": "Это был последний вопрос.",
                "is_last": True,
            }

        question_id = all_questions_ids[next_question_index]
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

    async def submit_test(
        self, telegram_id: int, course_id: int, user_answers: Dict[int, List[int]]
    ) -> Dict[str, Any]:
        """
        Обрабатывает ответы пользователя, подсчитывает результат и сохраняет его,
        если он лучше предыдущего.

        user_answers: Словарь, где ключ - ID вопроса, значение - список ID выбранных ответов.
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return {"success": False, "message": "Пользователь не найден."}

        course = await self.course_repo.get_by_id(course_id)
        if not course:
            return {"success": False, "message": "Курс не найден."}

        questions_in_db = await self.question_repo.get_questions_for_course(
            course_id, prefetch_answers=True
        )
        if not questions_in_db:
            return {"success": False, "message": "Вопросы для курса не найдены."}

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

        passed = score_percentage >= (course.min_test_percent_course or 90)

        # Получаем лучший предыдущий результат
        best_previous_test = await self.user_test_repo.get_best_user_test(
            user_id=user.id, course_id=course_id
        )

        should_save_current = True
        current_test_data_to_save = {
            "user_id": user.id,
            "course_id": course_id,
            "score": score_percentage,
            "is_complete": passed,
        }

        if best_previous_test:
            if passed:
                if not best_previous_test.complete:
                    should_save_current = True
                else:
                    if score_percentage <= best_previous_test.quantity_correct:
                        should_save_current = False
            else:
                if best_previous_test.complete:
                    should_save_current = False
                else:
                    if score_percentage <= best_previous_test.quantity_correct:
                        should_save_current = False

        final_score_percentage = score_percentage
        final_passed_status = passed
        final_correct_answers = correct_answers_count

        if should_save_current:
            await self.user_test_repo.update_or_create_user_test(
                **current_test_data_to_save
            )
        else:
            final_score_percentage = best_previous_test.quantity_correct
            final_passed_status = best_previous_test.complete
            final_correct_answers = int(
                round(best_previous_test.quantity_correct * total_questions_count / 100)
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
            "course_title": course.title,
            "score_percentage": final_score_percentage,
            "correct_answers_count": final_correct_answers,
            "total_questions_count": total_questions_count,
            "passed": final_passed_status,
            "min_test_percent_course": course.min_test_percent_course,
            "image_path": image_path,
        }
