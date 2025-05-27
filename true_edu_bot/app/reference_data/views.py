from django.shortcuts import render
from rest_framework import viewsets
from .models import JobTitle, Department
from .serializer import JobTitleSerializer, DepartmentSerializer


class JobTitleViewSet(viewsets.ModelViewSet):
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
