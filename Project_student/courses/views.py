from rest_framework import viewsets
from .models import Course, Student
from .serializers import CourseSerializer, StudentSerializer

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(active=True) #только активные курсы


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer