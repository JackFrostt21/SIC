from rest_framework import serializers
from app.learning_app.models.courses import TrainingCourse
from app.learning_app.models.testing import TopicQuestion, AnswerOption


class CourseTestAnswerSerializer(serializers.ModelSerializer):
    """Сериализатор для вариантов ответов в тесте"""

    class Meta:
        model = AnswerOption
        fields = ["id", "text", "is_correct", "order"]

    def to_representation(self, instance):
        """Фильтруем только актуальные ответы"""
        if not instance.is_actual:
            return None
        return super().to_representation(instance)


class CourseTestQuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для вопросов в тесте с вариантами ответов"""

    answer_options = serializers.SerializerMethodField()

    class Meta:
        model = TopicQuestion
        fields = ["id", "title", "is_multiple_choice", "order", "answer_options"]

    def get_answer_options(self, obj):
        """Получаем только актуальные варианты ответов, отсортированные по order"""
        actual_options = obj.answer_options.filter(is_actual=True).order_by("order")
        return CourseTestAnswerSerializer(actual_options, many=True).data


class CourseTestSerializer(serializers.ModelSerializer):
    """Сериализатор для получения теста курса"""

    questions = serializers.SerializerMethodField()

    class Meta:
        model = TrainingCourse
        fields = ["id", "title", "min_test_percent_course", "questions"]

    def get_questions(self, obj):
        """Получаем только актуальные вопросы, отсортированные по order"""
        actual_questions = obj.questions.filter(is_actual=True).order_by("order")
        return CourseTestQuestionSerializer(actual_questions, many=True).data


class TestSubmissionSerializer(serializers.Serializer):
    """Сериализатор для отправки результатов теста"""

    user_id = serializers.IntegerField(min_value=1)
    course_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    topic_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    quantity_correct = serializers.IntegerField(min_value=0, max_value=100)

    def validate(self, data):
        """Дополнительная валидация данных"""
        if data["quantity_correct"] < 0 or data["quantity_correct"] > 100:
            raise serializers.ValidationError(
                "quantity_correct должно быть в диапазоне 0-100"
            )
        course_id = data.get("course_id")
        topic_id = data.get("topic_id")
        if not course_id and not topic_id:
            raise serializers.ValidationError(
                "Нужно указать course_id или topic_id"
            )
        if course_id and topic_id:
            raise serializers.ValidationError(
                "Укажите либо course_id, либо topic_id, но не оба"
            )
        return data


class CertificateIssueResultSerializer(serializers.Serializer):
    """Результат попытки выдать сертификат после завершения теста."""

    status = serializers.CharField()
    id = serializers.IntegerField(allow_null=True)
    reason = serializers.CharField(allow_null=True)


class TestSubmissionResultSerializer(serializers.Serializer):
    """Сериализатор для результата отправки теста"""

    success = serializers.BooleanField()
    score = serializers.IntegerField()
    passed = serializers.BooleanField()
    message = serializers.CharField()
    course_title = serializers.CharField(required=False, allow_null=True)
    topic_title = serializers.CharField(required=False, allow_null=True)
    scope = serializers.CharField(required=False)
    certificate = CertificateIssueResultSerializer(required=False, allow_null=True)
