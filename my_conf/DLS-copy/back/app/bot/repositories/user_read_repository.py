from typing import List, Optional, Dict
from app.core.async_utils import AsyncRepository, AsyncUnitOfWork
from app.bot.models import UserRead, TelegramUser
from app.learning_app.models.courses import TrainingCourse, CourseTopic


class UserReadRepository(AsyncRepository[UserRead]):
    """
    Репозиторий для работы с отслеживанием прочтения материалов пользователями.
    Предоставляет асинхронные методы для операций с моделью UserRead.
    """
    def __init__(self):
        super().__init__(UserRead)
    
    async def mark_topic_as_read(self, user_id: int, course_id: int, topic_id: int) -> UserRead:
        """
        Отмечает тему как прочитанную пользователем.
        
        :param user_id: ID пользователя
        :param course_id: ID курса
        :param topic_id: ID темы
        :return: Объект записи о прочтении (новый или обновленный)
        """
        def _mark_as_read():
            user_read, created = UserRead.objects.update_or_create(
                user_id=user_id,
                course_id=course_id,
                topic_id=topic_id,
                defaults={'is_read': True}
            )
            return user_read
        
        return await AsyncUnitOfWork.execute(_mark_as_read)
    
    async def get_read_topics_for_course(self, user_id: int, course_id: int) -> List[int]:
        """
        Получает список ID прочитанных тем курса для пользователя.
        
        :param user_id: ID пользователя
        :param course_id: ID курса
        :return: Список ID прочитанных тем
        """
        def _get_read_topics():
            read_records = UserRead.objects.filter(
                user_id=user_id,
                course_id=course_id,
                is_read=True
            )
            return [record.topic_id for record in read_records]
        
        return await AsyncUnitOfWork.execute(_get_read_topics)
    
    async def get_read_status_for_topics(self, user_id: int, course_id: int, topic_ids: List[int]) -> Dict[int, bool]:
        """
        Получает статус прочтения для указанных тем.
        
        :param user_id: ID пользователя
        :param course_id: ID курса
        :param topic_ids: Список ID тем
        :return: Словарь {topic_id: is_read} с информацией о прочтении
        """
        def _get_read_status():
            # Получаем все записи о прочтении для указанных тем
            read_records = UserRead.objects.filter(
                user_id=user_id,
                course_id=course_id,
                topic_id__in=topic_ids
            )
            
            # Создаем словарь topic_id -> is_read
            result = {topic_id: False for topic_id in topic_ids}
            for record in read_records:
                result[record.topic_id] = record.is_read
                
            return result
        
        return await AsyncUnitOfWork.execute(_get_read_status)
    
    async def check_all_topics_read(self, user_id: int, course_id: int) -> bool:
        """
        Проверяет, прочитал ли пользователь все темы курса.
        
        :param user_id: ID пользователя
        :param course_id: ID курса
        :return: True, если все темы прочитаны, иначе False
        """
        def _check_all_read():
            # Получаем все активные темы курса
            all_topics = CourseTopic.objects.filter(
                training_course_id=course_id,
                is_actual=True
            )
            total_topics_count = all_topics.count()
            
            # Если тем нет, считаем курс прочитанным
            if total_topics_count == 0:
                return True
            
            # Получаем количество прочитанных тем
            read_topics_count = UserRead.objects.filter(
                user_id=user_id,
                course_id=course_id,
                is_read=True
            ).count()
            
            # Сравниваем количество
            return read_topics_count >= total_topics_count
        
        return await AsyncUnitOfWork.execute(_check_all_read)
    
    async def reset_read_status_for_course(self, user_id: int, course_id: int) -> None:
        """
        Сбрасывает статус прочтения всех тем курса для пользователя.
        
        :param user_id: ID пользователя
        :param course_id: ID курса
        """
        def _reset_read_status():
            UserRead.objects.filter(
                user_id=user_id,
                course_id=course_id
            ).update(is_read=False)
        
        await AsyncUnitOfWork.execute(_reset_read_status)