"""
Фабрика для создания структурированных callback_data
"""

import json
from typing import Dict, Any, Type, TypeVar
from pydantic import BaseModel
from app.bot.telegram.callback.schemas import RegistrationCallback, CourseMenuCallback


T = TypeVar("T", bound=BaseModel)



class CallbackFactory:
    """
    Фабрика для создания и парсинга callback_data
    """

    @staticmethod
    def create_callback_data(model: Type[T], **kwargs) -> str:
        """
        Создает callback_data из модели и параметров

        :param model: Класс модели Pydantic
        :param kwargs: Параметры для создания модели
        :return: JSON строка для callback_data
        """
        callback_instance = model(**kwargs)
        return callback_instance.model_dump_json()

    @staticmethod
    def parse_callback_data(callback_data: str, model: Type[T]) -> T:
        """
        Парсит callback_data в модель

        :param callback_data: JSON строка callback_data
        :param model: Класс модели Pydantic
        :return: Экземпляр модели
        """
        data = json.loads(callback_data)
        return model(**data)


# Вспомогательные функции для создания конкретных callback_data


def create_registration_callback(action: str) -> str:
    """
    Создает callback_data для регистрации

    :param action: Действие ("confirm", "edit", "skip", etc.)
    :return: JSON строка для callback_data
    """
    return CallbackFactory.create_callback_data(RegistrationCallback, action=action)


def create_course_menu_callback(action: str, course_id: int, **kwargs) -> str:
    """
    Создает callback_data для меню курса

    :param action: Действие ("topic", "list_topic", etc.)
    :param course_id: ID курса
    :param kwargs: Дополнительные параметры (topic_id, subtopic_id, page)
    :return: JSON строка для callback_data
    """
    return CallbackFactory.create_callback_data(
        CourseMenuCallback, action=action, course_id=course_id, **kwargs
    )
