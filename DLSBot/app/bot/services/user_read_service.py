from typing import List, Dict, Any, Optional
from app.bot.repositories.user_read_repository import UserReadRepository
from app.learning_app.repositories.course_repository import CourseRepository
from app.bot.repositories.telegram_user_repository import TelegramUserRepository


class UserReadService:
    """
    Сервис для работы с отслеживанием прочтения материалов пользователями.
    Содержит бизнес-логику отслеживания прогресса чтения.
    """
    def __init__(self):
        self.read_repository = UserReadRepository()
        self.course_repository = CourseRepository()
        self.user_repository = TelegramUserRepository()
    
    async def mark_topic_read(self, telegram_id: int, course_id: int, topic_id: int) -> Dict[str, Any]:
        """
        Отмечает тему как прочитанную пользователем.
        
        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :param topic_id: ID темы
        :return: Словарь с результатом операции
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Отмечаем тему как прочитанную
        user_read = await self.read_repository.mark_topic_as_read(user.id, course_id, topic_id)
        
        # Проверяем, все ли темы курса прочитаны
        all_read = await self.read_repository.check_all_topics_read(user.id, course_id)
        
        return {
            "success": True,
            "is_read": user_read.is_read,
            "all_topics_read": all_read,
            "message": "Тема отмечена как прочитанная"
        }
    
    async def get_course_reading_progress(self, telegram_id: int, course_id: int) -> Dict[str, Any]:
        """
        Получает прогресс чтения курса пользователем.
        
        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :return: Словарь с результатом операции
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Получаем курс и его темы
        course_data = await self.course_repository.get_course_with_topics(course_id)
        
        if not course_data:
            return {
                "success": False,
                "message": "Курс не найден"
            }
        
        # Получаем список ID тем курса
        topic_ids = [topic.id for topic in course_data['topics']]
        
        # Получаем статус прочтения для каждой темы
        read_status = await self.read_repository.get_read_status_for_topics(
            user.id, course_id, topic_ids
        )
        
        # Подсчитываем прогресс
        total_topics = len(topic_ids)
        read_topics = sum(1 for is_read in read_status.values() if is_read)
        
        if total_topics > 0:
            progress_percent = int((read_topics / total_topics) * 100)
        else:
            progress_percent = 100  # Если тем нет, считаем курс прочитанным на 100%
        
        # Формируем данные о темах с их статусом прочтения
        topics_with_status = [
            {
                "id": topic.id,
                "title": topic.name,
                "is_read": read_status.get(topic.id, False)
            }
            for topic in course_data['topics']
        ]
        
        return {
            "success": True,
            "course": {
                "id": course_data['course'].id,
                "title": course_data['course'].name
            },
            "progress": {
                "total_topics": total_topics,
                "read_topics": read_topics,
                "progress_percent": progress_percent,
                "all_read": read_topics == total_topics
            },
            "topics": topics_with_status
        }
    
    async def reset_reading_progress(self, telegram_id: int, course_id: int) -> Dict[str, Any]:
        """
        Сбрасывает прогресс чтения курса пользователем.
        
        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :return: Словарь с результатом операции
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if not user:
            return {
                "success": False,
                "message": "Пользователь не найден"
            }
        
        # Сбрасываем статус прочтения
        await self.read_repository.reset_read_status_for_course(user.id, course_id)
        
        return {
            "success": True,
            "message": "Прогресс чтения курса сброшен"
        }