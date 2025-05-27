from rest_framework import serializers
from .models import TrainingCourse, CourseTopic, CourseDirection, TopicQuestion, AnswerOption, ScormPack, NewsBlock, TagCourse, Company, Certificate, RatingTrainingCourse, CourseDeadline
from app.bot.models.telegram_user import TelegramUser, TelegramGroup, UserRead
from app.bot.models.testing_module import UserTest


class TrainingCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCourse
        fields = '__all__'


class CourseTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTopic
        fields = '__all__'


class CourseDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDirection
        fields = '__all__'


class TopicQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicQuestion
        fields = '__all__'


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = '__all__'


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = '__all__'


class TelegramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramGroup
        fields = '__all__'


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRead
        fields = '__all__'


class UserTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTest
        fields = '__all__'


class ScormPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScormPack
        fields = '__all__'


class NewsBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsBlock
        fields = '__all__'


class TagCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagCourse
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


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