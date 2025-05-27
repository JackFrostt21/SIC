from django.shortcuts import render
from rest_framework import viewsets
from .models import JobTitle, Department, Company, SettingsBot
from .serializer import JobTitleSerializer, DepartmentSerializer, CompanySerializer, SettingsBotSerializer


class JobTitleViewSet(viewsets.ModelViewSet):
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer 


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer    


class SettingsBotViewSet(viewsets.ModelViewSet):
    queryset = SettingsBot.objects.all()
    serializer_class = SettingsBotSerializer

