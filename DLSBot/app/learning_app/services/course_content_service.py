from typing import Dict, Any, Optional, List
import os
from app.bot.repositories.telegram_user_repository import TelegramUserRepository
from app.bot.repositories.user_read_repository import UserReadRepository
from app.learning_app.repositories.course_repository import CourseRepository
from app.learning_app.repositories.topic_repository import TopicRepository


class CourseContentService:
    """
    Сервис для работы с контентом курсов.
    Содержит бизнес-логику для доступа и отображения содержимого курсов.
    """

    def __init__(self):
        self.user_repository = TelegramUserRepository()
        self.read_repository = UserReadRepository()
        self.course_repository = CourseRepository()
        self.topic_repository = TopicRepository()

    async def get_course_content(
        self, telegram_id: int, course_id: int
    ) -> Dict[str, Any]:
        """
        Получает информацию о курсе и его темах для отображения в меню.

        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :return: Словарь с данными о курсе и его темах
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)

        if not user:
            return {"success": False, "message": "Пользователь не найден"}

        # TODO: Мне нужно получить курс и его темы, а также статус теста
        # CourseRepository.get_course_with_topics нужно доработать,
        # чтобы он возвращал и статус теста, либо я сделаю это отдельным запросом.
        # ??? get_course_with_topics теперь также возвращает test_status и test_score
        # Это изменение мне нужно будет сделать в CourseRepository.get_course_with_topics
        course_data_from_repo = await self.course_repository.get_course_with_topics(
            course_id, user.id
        )  # Передаем user.id

        if not course_data_from_repo or not course_data_from_repo.get("course"):
            return {"success": False, "message": "Курс не найден"}

        # Получаем статус прочтения для каждой темы
        topic_ids = [topic.id for topic in course_data_from_repo["topics"]]
        read_status = await self.read_repository.get_read_status_for_topics(
            user.id, course_id, topic_ids
        )

        # Формируем данные о темах с их статусом прочтения
        topics_with_status = [
            {
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "order": topic.order,
                "is_read": read_status.get(topic.id, False),
                "has_content": bool(topic.main_text),
                "has_pdf": bool(topic.pdf_file and topic.pdf_file_readuser),
                "has_audio": bool(topic.audio_file and topic.audio_file_readuser),
                "has_video": bool(topic.video_file and topic.video_file_readuser),
            }
            for topic in course_data_from_repo["topics"]
        ]

        # Сортируем темы по порядку
        topics_with_status.sort(key=lambda x: x["order"])

        return {
            "success": True,
            "course": {
                "id": course_data_from_repo["course"].id,
                "title": course_data_from_repo["course"].title,
                "description": course_data_from_repo["course"].description,
                "logo": (
                    course_data_from_repo["course"].image_course.url
                    if course_data_from_repo["course"].image_course
                    else None
                ),
                "test_status": course_data_from_repo.get("test_status"),
                "test_score": course_data_from_repo.get("test_score"),
            },
            "topics": topics_with_status,
            "topics_count": len(topics_with_status),
        }

    async def get_topic_content(
        self, telegram_id: int, course_id: int, topic_id: int
    ) -> Dict[str, Any]:
        """
        Получает содержимое темы курса.

        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :param topic_id: ID темы
        :return: Словарь с содержимым темы и метаданными
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)

        if not user:
            return {"success": False, "message": "Пользователь не найден"}

        # Получаем тему
        topic = await self.topic_repository.get_by_id(topic_id)

        if not topic:
            return {"success": False, "message": "Тема не найдена"}

        # Проверяем, что тема принадлежит указанному курсу
        if topic.training_course_id != course_id:
            return {"success": False, "message": "Тема не принадлежит указанному курсу"}

        # Отмечаем тему как прочитанную
        await self.read_repository.mark_topic_as_read(user.id, course_id, topic_id)

        # Формируем данные о контенте
        content_data = {
            "id": topic.id,
            "title": topic.title,
            "description": topic.description,
            "text_content": topic.main_text,
            "image_url": (
                topic.image_course_topic.url if topic.image_course_topic else None
            ),
            "image_path": (
                topic.image_course_topic.path
                if topic.image_course_topic
                and hasattr(topic.image_course_topic, "path")
                else None
            ),
            "main_text_readuser": topic.main_text_readuser,
            "main_text_webapp_readuser": topic.main_text_webapp_readuser,
            "has_pdf": bool(topic.pdf_file and topic.pdf_file_readuser),
            "has_audio": bool(topic.audio_file and topic.audio_file_readuser),
            "has_video": bool(topic.video_file and topic.video_file_readuser),
            "pdf_file": (
                topic.pdf_file.url
                if topic.pdf_file and topic.pdf_file_readuser
                else None
            ),
            "audio_file": (
                topic.audio_file.url
                if topic.audio_file and topic.audio_file_readuser
                else None
            ),
            "video_file": (
                topic.video_file.url
                if topic.video_file and topic.video_file_readuser
                else None
            ),
            "course_id": course_id,
        }

        return {
            "success": True,
            "content": content_data,
            "is_read": True,  # Мы только что отметили как прочитанную
        }

    async def get_pdf_file(
        self, telegram_id: int, course_id: int, topic_id: int
    ) -> Dict[str, Any]:
        """
        Получает PDF-файл темы курса.

        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :param topic_id: ID темы
        :return: Словарь с информацией о PDF-файле
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)

        if not user:
            return {"success": False, "message": "Пользователь не найден"}

        # Получаем тему
        topic = await self.topic_repository.get_by_id(topic_id)

        if not topic:
            return {"success": False, "message": "Тема не найдена"}

        # Проверяем наличие PDF-файла и разрешение на его чтение
        if not (topic.pdf_file and topic.pdf_file_readuser):
            return {"success": False, "message": "PDF-файл недоступен"}

        # Проверяем существование файла
        pdf_path = topic.pdf_file.path
        if not os.path.exists(pdf_path):
            return {"success": False, "message": "Файл не найден на сервере"}

        return {
            "success": True,
            "file_info": {
                "path": pdf_path,
                "title": topic.title,
                "filename": os.path.basename(pdf_path),
            },
        }

    async def get_audio_file(
        self, telegram_id: int, course_id: int, topic_id: int
    ) -> Dict[str, Any]:
        """
        Получает аудио-файл темы курса.

        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :param topic_id: ID темы
        :return: Словарь с информацией об аудио-файле
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)

        if not user:
            return {"success": False, "message": "Пользователь не найден"}

        # Получаем тему
        topic = await self.topic_repository.get_by_id(topic_id)

        if not topic:
            return {"success": False, "message": "Тема не найдена"}

        # Проверяем наличие аудио-файла и разрешение на его прослушивание
        if not (topic.audio_file and topic.audio_file_readuser):
            return {"success": False, "message": "Аудио-файл недоступен"}

        # Проверяем существование файла
        audio_path = topic.audio_file.path
        if not os.path.exists(audio_path):
            return {"success": False, "message": "Файл не найден на сервере"}

        return {
            "success": True,
            "file_info": {
                "path": audio_path,
                "title": topic.title,
                "filename": os.path.basename(audio_path),
            },
        }

    async def get_video_file(
        self, telegram_id: int, course_id: int, topic_id: int
    ) -> Dict[str, Any]:
        """
        Получает видео-файл темы курса.

        :param telegram_id: Telegram ID пользователя
        :param course_id: ID курса
        :param topic_id: ID темы
        :return: Словарь с информацией о видео-файле
        """
        user = await self.user_repository.get_by_telegram_id(telegram_id)

        if not user:
            return {"success": False, "message": "Пользователь не найден"}

        # Получаем тему
        topic = await self.topic_repository.get_by_id(topic_id)

        if not topic:
            return {"success": False, "message": "Тема не найдена"}

        # Проверяем наличие видео-файла и разрешение на его просмотр
        if not (topic.video_file and topic.video_file_readuser):
            return {"success": False, "message": "Видео-файл недоступен"}

        # Проверяем существование файла
        video_path = topic.video_file.path
        if not os.path.exists(video_path):
            return {"success": False, "message": "Файл не найден на сервере"}

        return {
            "success": True,
            "file_info": {
                "path": video_path,
                "title": topic.title,
                "filename": os.path.basename(video_path),
            },
        }
