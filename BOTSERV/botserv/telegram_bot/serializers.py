from rest_framework import serializers
from .models import Applications, TelegramUser ###DirectoryServices, BuildingEriell, FloorEriell, BlockEriell,

class ApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applications
        fields = [
            'user_fio', 'user_eriell', 'name_services', 'building', 'floor', 'block',
              'office_workplace', 'internal_number', 'mobile_phone', 'application_text'
        ]


class TelegramUserSerializer(serializers.ModelSerializer):
    user_fio = serializers.CharField(required=False)
    user_eriell = serializers.CharField(required=False)
    internal_number = serializers.CharField(required=False)
    mobile_phone = serializers.CharField(required=False)

    class Meta:
        model = TelegramUser
        fields = [
            'id', 'user_fio', 'user_eriell', 'email', 'number_user_telegram', 'internal_number', 'mobile_phone'
        ]

# class DirectoryServicesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DirectoryServices
#         fields = [
#             'id_servises_dir_serv', 'name_services'
#         ]

# class BuildingEriellSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BuildingEriell
#         fields = [
#             'id_servises_building', 'adress_building'
#         ]

# class FloorEriellSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FloorEriell
#         fields = [
#             'id_servises_floor', 'number_floor'
#         ]

# class BlockEriellSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BlockEriell
#         fields = [
#             'id_servises_block', 'number_block'
#         ]  