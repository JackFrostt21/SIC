from django.db import models

class TelegramUser(models.Model):
    user_eriell = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100)
    number_user_telegram = models.CharField(max_length=100)
    internal_number = models.CharField(max_length=100, null=True)
    mobile_phone = models.CharField(max_length=100, null=True)
    user_fio = models.CharField(max_length=100, null=True)


class DirectoryServices(models.Model):
    id_servises_dir_serv = models.CharField(primary_key=True, max_length=100) 
    name_services = models.CharField(max_length=100, null=True)

class Applications(models.Model):
    user_fio = models.CharField(max_length=100, null=True)
    user_eriell = models.CharField(max_length=100, null=True)
    name_services = models.CharField(max_length=100, null=True)
    building = models.CharField(max_length=100, null=True)
    floor = models.CharField(max_length=100, null=True)
    block = models.CharField(max_length=100, null=True)
    office_workplace = models.CharField(max_length=100, null=True)      
    internal_number = models.CharField(max_length=100, null=True)       
    mobile_phone = models.CharField(max_length=100, null=True)          
    application_text = models.TextField(null=True)

class BuildingEriell(models.Model):
    id_servises_building = models.CharField(primary_key=True, max_length=100)
    adress_building = models.CharField(max_length=100, null=True)

class FloorEriell(models.Model):
    id_servises_floor = models.CharField(primary_key=True, max_length=100)
    number_floor = models.CharField(max_length=100, null=True)

class BlockEriell(models.Model):
    id_servises_block = models.CharField(primary_key=True, max_length=100)
    number_block = models.CharField(max_length=100, null=True)



