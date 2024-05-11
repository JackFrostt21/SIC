from rest_framework import serializers
from .models import TrainingCourse, CourseTopic


class TopicCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTopic
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCourse
        fields = "__all__"
