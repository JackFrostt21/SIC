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


    def validate(self, data):
        if self.instance:
            if not self.instance.is_actual:
                if 'user' in data or 'group' in data:
                    raise serializers.ValidationError("Cannot modify users or groups for inactive course")
        return data 
