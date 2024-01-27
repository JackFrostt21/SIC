from django.db import models

class User(models.Model):
    user_eriell = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    username_telegram = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=False)

class DirectoryServices(models.Model):
    name_services = models.CharField(max_length=100)

class ApplicationForm(models.Model):
    name_services = models.ForeignKey(DirectoryServices, on_delete=models.PROTECT)
    floor = models.IntegerField(max_length=50)
    block = models.CharField(max_length=50)
    office_workplace = models.CharField(max_length=100)
    internal_number = models.IntegerField(max_length=50)
    mobile_phone = models.IntegerField(max_length=50)
    application_text = models.TextField()

class Applications(models.Model):
    name_services = models.ForeignKey(DirectoryServices, on_delete=models.PROTECT)
    application_text = models.TextField()
    application_from = models.DateTimeField()
    answer = models.TextField()
    time_answer = models.DateTimeField()
    status = models.CharField(max_length=100)