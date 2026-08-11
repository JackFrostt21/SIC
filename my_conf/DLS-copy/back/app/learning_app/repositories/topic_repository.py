from typing import List, Optional
from app.core.async_utils import AsyncRepository
from app.learning_app.models.courses import CourseTopic


class TopicRepository(AsyncRepository[CourseTopic]):
    """
    Репозиторий для работы с темами курсов.
    """

    def __init__(self):
        super().__init__(CourseTopic)

    async def get_topics_for_course(
        self, course_id: int, is_actual: bool = True
    ) -> List[CourseTopic]:
        """
        Получает список тем для указанного курса.

        Args:
            course_id: ID курса.
            is_actual: Флаг, указывающий, следует ли получать только актуальные темы.

        Returns:
            Список объектов CourseTopic.
        """
        return await self.filter(training_course_id=course_id, is_actual=is_actual)
