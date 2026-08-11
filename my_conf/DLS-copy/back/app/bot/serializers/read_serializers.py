from rest_framework import serializers
from app.bot.models.education_data import UserRead
from app.bot.models.telegram_user import TelegramUser
from app.learning_app.models.courses import TrainingCourse, CourseTopic


class CourseReadTopicSerializer(serializers.Serializer):
    """Сериализатор для темы курса с информацией о прочтении"""

    id = serializers.IntegerField()
    title = serializers.CharField()
    order = serializers.IntegerField()
    is_read = serializers.BooleanField()
    read_at = serializers.DateTimeField(allow_null=True)


class CourseReadCourseSerializer(serializers.Serializer):
    """Сериализатор для курса с темами и статистикой прочтения"""

    id = serializers.IntegerField()
    title = serializers.CharField()
    topics = CourseReadTopicSerializer(many=True)
    total_topics = serializers.IntegerField()
    read_topics = serializers.IntegerField()
    progress_percent = serializers.IntegerField()


class CourseReadListSerializer(serializers.Serializer):
    """Сериализатор для списка курсов пользователя с информацией о прочтении"""

    telegram_user_id = serializers.IntegerField()
    full_name = serializers.CharField()
    courses = CourseReadCourseSerializer(many=True)


class MarkTopicReadSerializer(serializers.Serializer):
    """Сериализатор для запроса на отметку темы как прочитанной"""

    is_read = serializers.BooleanField()

    def validate_is_read(self, value):
        """Валидация поля is_read"""
        if not isinstance(value, bool):
            raise serializers.ValidationError("is_read должно быть boolean значением")
        return value


class MarkTopicReadResultSerializer(serializers.Serializer):
    """Сериализатор для результата отметки темы как прочитанной"""

    success = serializers.BooleanField()
    message = serializers.CharField()
    topic_title = serializers.CharField()
    read_at = serializers.DateTimeField(allow_null=True)


class UnfinishedCourseSerializer(serializers.Serializer):
    """Сериализатор для непройденного курса (минимальная информация)"""

    id = serializers.IntegerField()
    title = serializers.CharField()
    test_status = serializers.CharField(allow_null=True)


class UnfinishedCoursesListSerializer(serializers.Serializer):
    """Сериализатор для списка непройденных курсов пользователя"""

    telegram_user_id = serializers.IntegerField()
    full_name = serializers.CharField()
    courses = UnfinishedCourseSerializer(many=True)
