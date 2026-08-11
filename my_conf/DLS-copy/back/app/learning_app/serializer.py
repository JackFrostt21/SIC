from rest_framework import serializers
from django.utils.html import strip_tags
from drf_spectacular.utils import extend_schema_field
from .models.additional import (
    Certificate,
    RatingTrainingCourse,
    CourseDeadline,
    NewsBlock,
)
from .models.courses import (
    TagCourse,
    CourseDirection,
    TrainingCourse,
    CourseTopic,
)
from .models.testing import TopicQuestion, AnswerOption


class TrainingCourseSerializer(serializers.ModelSerializer):
    deadline = serializers.DateField(read_only=True, required=False)
    completed = serializers.SerializerMethodField(
        help_text="Пользователь завершил курс"
    )

    class Meta:
        model = TrainingCourse
        fields = "__all__"
        extra_fields = ["completed"]

    @extend_schema_field(serializers.BooleanField())
    def get_completed(self, obj):
        user_id = self.context.get("user_id")
        if not user_id:
            return False
        from app.bot.models.education_data import UserTest

        return UserTest.objects.filter(
            user_id=user_id, training=obj, complete=True
        ).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Преобразуем относительный URL изображения в абсолютный
        if data.get("image_course"):
            request = self.context.get("request")
            if request:
                data["image_course"] = request.build_absolute_uri(data["image_course"])
        return data


class AvailableTrainingCourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для открытых курсов (самозапись).
    Добавляет флаги already_enrolled и can_enroll.
    """

    completed = serializers.SerializerMethodField(
        help_text="Пользователь завершил курс"
    )
    already_enrolled = serializers.SerializerMethodField(
        help_text="Пользователь уже назначен на курс"
    )
    can_enroll = serializers.SerializerMethodField(
        help_text="Пользователь может самозаписаться на курс"
    )
    image_course = serializers.SerializerMethodField(
        help_text="Абсолютный URL изображения курса"
    )

    class Meta:
        model = TrainingCourse
        fields = [
            "id",
            "title",
            "description",
            "course_direction",
            "open_course",
            "is_actual",
            "archive",
            "image_course",
            "tag",
            "completed",
            "already_enrolled",
            "can_enroll",
        ]
        read_only_fields = [
            "completed",
            "already_enrolled",
            "can_enroll",
            "image_course",
        ]

    @extend_schema_field(serializers.BooleanField())
    def get_completed(self, obj):
        user_id = self.context.get("user_id")
        if not user_id:
            return False
        from app.bot.models.education_data import UserTest

        return UserTest.objects.filter(
            user_id=user_id, training=obj, complete=True
        ).exists()

    @extend_schema_field(serializers.BooleanField())
    def get_already_enrolled(self, obj):
        assigned_ids = self.context.get("assigned_course_ids")
        if isinstance(assigned_ids, set):
            return obj.id in assigned_ids
        return False

    @extend_schema_field(serializers.BooleanField())
    def get_can_enroll(self, obj):
        if obj.archive or not obj.is_actual or not getattr(obj, "open_course", False):
            return False
        return not self.get_already_enrolled(obj)

    def get_image_course(self, obj):
        if not getattr(obj, "image_course", None):
            return None
        # Получаем request из контекста и строим абсолютный URL
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image_course.url)
        return obj.image_course.url


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = "__all__"


class RatingTrainingCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingTrainingCourse
        fields = "__all__"


class CourseDeadlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDeadline
        fields = "__all__"


class NewsBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsBlock
        fields = "__all__"


class NewsBlockListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    is_important = serializers.BooleanField(read_only=True)
    date = serializers.DateField(source="start_date_news", read_only=True)
    preview = serializers.SerializerMethodField()
    is_pinned = serializers.BooleanField(read_only=True, default=False)
    is_read = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = NewsBlock
        fields = [
            "id",
            "is_important",
            "date",
            "preview",
            "is_pinned",
            "is_read",
        ]

    @extend_schema_field(serializers.CharField())
    def get_preview(self, obj):
        raw_html = obj.text_news or ""
        text = strip_tags(raw_html)
        max_len = 180
        if len(text) <= max_len:
            return text
        return text[:max_len].rstrip() + "…"


class NewsBlockDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(source="news_title", read_only=True)
    date = serializers.DateField(source="start_date_news", read_only=True)
    is_important = serializers.BooleanField(read_only=True)
    text = serializers.CharField(source="text_news", read_only=True)

    class Meta:
        model = NewsBlock
        fields = ["id", "name", "date", "is_important", "text"]


class NewsReadResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    is_read = serializers.BooleanField()
    is_pinned = serializers.BooleanField()


class NewsReadRequestSerializer(serializers.Serializer):
    is_read = serializers.BooleanField()


class NewsPinRequestSerializer(serializers.Serializer):
    is_pinned = serializers.BooleanField()


class NewsPinResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    is_pinned = serializers.BooleanField()


class EnrollTrainingCourseResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    enrolled = serializers.BooleanField()
    already_enrolled = serializers.BooleanField()
    course = AvailableTrainingCourseSerializer()


class TagCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagCourse
        fields = "__all__"


class CourseDirectionSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()

    class Meta:
        model = CourseDirection
        fields = [
            "id",
            "title",
            "is_actual",
            "created_at",
            "updated_at",
            "courses",
        ]

    @extend_schema_field(TrainingCourseSerializer(many=True))
    def get_courses(self, obj):
        # The view will prefetch related active courses.
        return TrainingCourseSerializer(
            obj.trainingcourse_set.all(), many=True, context=self.context
        ).data


class CourseTopicSerializer(serializers.ModelSerializer):
    has_scorm = serializers.BooleanField(
        read_only=True,
        help_text="У темы есть актуальный SCORM-пакет",
    )

    class Meta:
        model = CourseTopic
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Преобразуем относительные URL в абсолютные
        request = self.context.get("request")
        if request:
            if data.get("image_course_topic"):
                data["image_course_topic"] = request.build_absolute_uri(
                    data["image_course_topic"]
                )
            if data.get("pdf_file"):
                data["pdf_file"] = request.build_absolute_uri(data["pdf_file"])
            if data.get("audio_file"):
                data["audio_file"] = request.build_absolute_uri(data["audio_file"])
            if data.get("video_file"):
                data["video_file"] = request.build_absolute_uri(data["video_file"])
        return data


class TopicQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicQuestion
        fields = "__all__"


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = "__all__"
