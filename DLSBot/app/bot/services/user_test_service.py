from typing import List, Dict, Any, Optional
from app.bot.repositories.user_test_repository import UserTestRepository
# from app.learning_app.repositories.test_repository import TestRepository
from app.bot.repositories.telegram_user_repository import TelegramUserRepository


class UserTestService:
    """
    Сервис для работы с тестированием пользователей.
    Содержит бизнес-логику процесса тестирования.
    """
    def __init__(self):
        self.test_repository = UserTestRepository()
        # self.question_repository = TestRepository()
        self.user_repository = TelegramUserRepository()
    
    async def start_test(self, telegram_id: int, course_id: int) -> Dict[str, Any]:
        """
        Начинает тестирование для пользователя по курсу.
        
        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :return: Словарь с результатом операции и первым вопросом
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Получаем или создаем тест
        test = await self.test_repository.get_or_create_test(user.id, course_id)
        
        # Получаем первый вопрос теста
        questions = await self.question_repository.get_questions_for_course(course_id)
        
        if not questions:
            return {
                "success": False,
                "message": "В курсе нет вопросов для тестирования"
            }
        
        first_question = questions[0]
        
        # Получаем варианты ответов для первого вопроса
        answers = await self.question_repository.get_answers_for_question(first_question.id)
        
        return {
            "success": True,
            "test_id": test.id,
            "question": {
                "id": first_question.id,
                "title": first_question.title,
                "is_multiple_choice": first_question.is_multiple_choice,
                "order": first_question.order,
                "answers": [
                    {
                        "id": answer.id,
                        "text": answer.text,
                        "number": answer.number
                    }
                    for answer in answers
                ]
            },
            "total_questions": len(questions),
            "current_index": 0,
            "message": "Тестирование начато"
        }
    
    async def submit_answer(self, 
                          telegram_id: int, 
                          course_id: int, 
                          question_id: int, 
                          answer_ids: List[str]) -> Dict[str, Any]:
        """
        Сохраняет ответ пользователя на вопрос теста.
        
        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :param question_id: ID вопроса
        :param answer_ids: Список ID выбранных ответов
        :return: Словарь с результатом операции
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Получаем информацию о вопросе
        question = await self.question_repository.get_question_by_id(question_id)
        
        if not question:
            return {
                "success": False,
                "message": "Вопрос не найден"
            }
        
        # Сохраняем ответ
        await self.test_repository.save_answer(
            user.id, 
            course_id, 
            question_id, 
            answer_ids, 
            question.is_multiple_choice
        )
        
        # Получаем все вопросы курса для определения следующего вопроса
        questions = await self.question_repository.get_questions_for_course(course_id)
        
        # Находим индекс текущего вопроса
        current_index = next((i for i, q in enumerate(questions) if q.id == question_id), -1)
        
        # Определяем, есть ли следующий вопрос
        has_next = current_index < len(questions) - 1
        next_question = questions[current_index + 1] if has_next else None
        
        result = {
            "success": True,
            "answer_submitted": True,
            "current_index": current_index,
            "total_questions": len(questions),
            "has_next_question": has_next
        }
        
        # Если есть следующий вопрос, добавляем информацию о нем
        if next_question:
            answers = await self.question_repository.get_answers_for_question(next_question.id)
            result["next_question"] = {
                "id": next_question.id,
                "title": next_question.title,
                "is_multiple_choice": next_question.is_multiple_choice,
                "order": next_question.order,
                "answers": [
                    {
                        "id": answer.id,
                        "text": answer.text,
                        "number": answer.number
                    }
                    for answer in answers
                ]
            }
            result["message"] = "Ответ сохранен, переход к следующему вопросу"
        else:
            result["message"] = "Ответ сохранен, это был последний вопрос"
        
        return result
    
    async def get_question(self, 
                         telegram_id: int, 
                         course_id: int, 
                         question_index: int) -> Dict[str, Any]:
        """
        Получает вопрос теста по его индексу.
        
        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :param question_index: Индекс вопроса
        :return: Словарь с результатом операции и данными вопроса
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Получаем все вопросы курса
        questions = await self.question_repository.get_questions_for_course(course_id)
        
        if not questions:
            return {
                "success": False,
                "message": "В курсе нет вопросов для тестирования"
            }
        
        # Проверяем, что индекс в допустимом диапазоне
        if question_index < 0 or question_index >= len(questions):
            return {
                "success": False,
                "message": "Недопустимый индекс вопроса"
            }
        
        # Получаем вопрос по индексу
        question = questions[question_index]
        
        # Получаем варианты ответов
        answers = await self.question_repository.get_answers_for_question(question.id)
        
        # Получаем ранее выбранные ответы пользователя
        selected_answers = await self.test_repository.get_selected_answers(
            user.id, course_id, question.id
        )
        
        return {
            "success": True,
            "question": {
                "id": question.id,
                "title": question.title,
                "is_multiple_choice": question.is_multiple_choice,
                "order": question.order,
                "answers": [
                    {
                        "id": answer.id,
                        "text": answer.text,
                        "number": answer.number,
                        "is_selected": str(answer.id) in selected_answers
                    }
                    for answer in answers
                ]
            },
            "total_questions": len(questions),
            "current_index": question_index,
            "has_prev": question_index > 0,
            "has_next": question_index < len(questions) - 1
        }
    
    async def finish_test(self, telegram_id: int, course_id: int) -> Dict[str, Any]:
        """
        Завершает тестирование и подсчитывает результаты.
        
        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :return: Словарь с результатами теста
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Проверяем, что тест существует
        test = await self.test_repository.get_test_result(user.id, course_id)
        
        if not test:
            return {
                "success": False,
                "message": "Тест не найден"
            }
        
        # Подсчитываем результаты теста
        results = await self.test_repository.count_results(user.id, course_id)
        
        return {
            "success": True,
            "test_completed": True,
            "results": results,
            "message": (
                f"Тест завершен. "
                f"Правильных ответов: {results['correct_percent']}%, "
                f"неправильных: {results['incorrect_percent']}%"
            )
        }
    
    async def get_test_results(self, telegram_id: int, course_id: int) -> Dict[str, Any]:
        """
        Получает результаты тестирования пользователя по курсу.
        
        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :return: Словарь с результатами теста
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Получаем результаты теста
        test = await self.test_repository.get_test_result(user.id, course_id)
        
        if not test:
            return {
                "success": False,
                "message": "Тест не найден или не был пройден"
            }
        
        # Получаем детальные результаты
        results = {
            "test_id": test.id,
            "course_id": test.training_id,
            "user_id": test.user_id,
            "is_complete": test.complete,
            "correct_percent": test.quantity_correct,
            "incorrect_percent": test.quantity_not_correct,
            "answers_count": len(test.user_answer["results"]),
            "passed": test.complete
        }
        
        return {
            "success": True,
            "test_exists": True,
            "results": results
        }
    
    async def get_completed_tests(self, telegram_id: int) -> Dict[str, Any]:
        """
        Получает список успешно пройденных пользователем тестов.
        
        :param telegram_id: Telegram ID пользователя
        :return: Словарь со списком пройденных тестов
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Получаем список ID курсов с пройденными тестами
        completed_course_ids = await self.test_repository.get_completed_courses(user.id)
        
        if not completed_course_ids:
            return {
                "success": True,
                "completed_tests": [],
                "count": 0,
                "message": "У пользователя нет пройденных тестов"
            }
        
        # Получаем информацию о курсах
        completed_courses = []
        for course_id in completed_course_ids:
            test = await self.test_repository.get_test_result(user.id, course_id)
            course_data = await self.course_repository.get_by_id(course_id)
            
            if course_data and test:
                completed_courses.append({
                    "course_id": course_id,
                    "course_title": course_data.name,
                    "correct_percent": test.quantity_correct,
                    "completed_at": test.updated_at.isoformat() if test.updated_at else None
                })
        
        return {
            "success": True,
            "completed_tests": completed_courses,
            "count": len(completed_courses)
        }