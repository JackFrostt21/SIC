from rest_framework import serializers
from .models import JobTitle, Department, Company, SettingsBot


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class SettingsBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsBot
        fields = '__all__'

