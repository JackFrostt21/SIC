from rest_framework import serializers
from .models.additional import Certificate, RatingTrainingCourse, CourseDeadline, NewsBlock
from .models.courses import TagCourse, CourseDirection, TrainingCourse, CourseTopic, ScormPack
from .models.testing import TopicQuestion, AnswerOption


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'


class RatingTrainingCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingTrainingCourse
        fields = '__all__'


class CourseDeadlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDeadline
        fields = '__all__'


class NewsBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsBlock
        fields = '__all__'


class TagCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagCourse
        fields = '__all__'


class CourseDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDirection
        fields = '__all__'


class TrainingCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCourse
        fields = '__all__'


class CourseTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTopic
        fields = '__all__'


class ScormPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScormPack
        fields = '__all__'


class TopicQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicQuestion
        fields = '__all__'


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = '__all__'
