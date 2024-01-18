from django.db import models

class Course(models.Model):
    course_name = models.CharField(max_length=160)
    data_start = models.DateField()
    data_end = models.DateField()
    active = models.BooleanField()


class Student(models.Model):
    telegram_username = models.CharField(max_length=100)
    student_username = models.CharField(max_length=160)
    email = models.EmailField()
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
