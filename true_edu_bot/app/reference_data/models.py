from django.db import models


class JobTitle(models.Model):
    name = models.CharField(max_length=100, verbose_name='Должность')
    source_id = models.CharField(max_length=100, verbose_name='ГУИД 1С', blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['name']
    

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name='Подразделение')
    source_id = models.CharField(max_length=100, verbose_name='ГУИД 1С', blank=True, null=True)
    jobtitle = models.ManyToManyField(JobTitle, verbose_name='Должность', related_name='jobtitle_department', blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        ordering = ['name']