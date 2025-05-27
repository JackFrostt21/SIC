"""
Pydantic-модели для структурированных callback_data
"""

from aiogram.filters.callback_data import CallbackData
from typing import Optional


class RegistrationCallback(CallbackData, prefix="rc"):
    """
    Модель для callback_data в процессе регистрации
    """

    action: str  # "confirm", "edit", "skip", "edit_name", "edit_phone", "edit_email", "edit_birth_date"


class CourseMenuCallback(CallbackData, prefix="cm"):
    """
    Модель для callback_data в меню курса
    """

    action: str  # "topic", "list_topics", "content_text", "show_results"
    course_id: int
    topic_id: Optional[int] = None
    page: int = 0
