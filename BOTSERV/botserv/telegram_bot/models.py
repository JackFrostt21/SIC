from django.db import models

class TelegramUser(models.Model):
    user_eriell = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    username_telegram = models.CharField(max_length=100)        # поменять на ID телеграм
    active = models.BooleanField(default=False) #тоже получаю от Димы, добавить к проверке для работы с заявками. Проговорить еще раз логику, пока не понял как корректно устанавливать если только не от Димы
    internal_number = models.CharField(max_length=100, null=True)   #тоже получаю от Димы, добавить проверку при формировании заявки
    mobile_phone = models.CharField(max_length=100, null=True)      #тоже получаю от Димы, добавить проверку при формировании заявки

class DirectoryServices(models.Model):
    name_services = models.CharField(max_length=100, null=True)

class ApplicationForm(models.Model):
    name_services = models.ForeignKey(DirectoryServices, on_delete=models.PROTECT, null=True)
    floor = models.IntegerField(max_length=50)
    block = models.CharField(max_length=50)
    office_workplace = models.CharField(max_length=100)
    internal_number = models.IntegerField(max_length=50)
    mobile_phone = models.IntegerField(max_length=50)
    application_text = models.TextField()

class Applications(models.Model):
    user_eriell = models.CharField(max_length=100, null=True)
    name_services = models.CharField(max_length=100, null=True)
    building = models.CharField(max_length=100, null=True)      #как инлайн кнопки
    floor = models.CharField(max_length=100, null=True)         #как инлайн кнопки
    block = models.CharField(max_length=100, null=True)         #как инлайн кнопки
    office_workplace = models.CharField(max_length=100, null=True)
    internal_number = models.CharField(max_length=100, null=True)
    mobile_phone = models.CharField(max_length=100, null=True)
    application_text = models.TextField(null=True) 
    
    #building потом этаж потом блок (выводить только доступные в инлайн кнопки)

    #продумать отправку в чат бот по ответственным name_services(сейчас механизм у ребят есть), как вариант