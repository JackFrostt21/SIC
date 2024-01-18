from rest_framework import serializers
from .models import Course, Student

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 
                  'course_name', 
                  'data_start', 
                  'data_end', 
                  'active']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 
                  'telegram_username', 
                  'student_username', 
                  'email', 
                  'course']