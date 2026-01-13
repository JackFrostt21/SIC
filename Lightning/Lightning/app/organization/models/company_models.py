from django.db import models


class Company(models.Model):
    """Компания"""
    name = models.CharField(max_length=255, verbose_name='Название компании')
    logo = models.ImageField(upload_to='companies/logos/', null=True, blank=True, verbose_name='Логотип компании')

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
        ordering = ['name']

    def __str__(self):
        return self.name


class JobTitle(models.Model):
    """Должность"""
    name = models.CharField(max_length=255, unique=True, verbose_name='Название должности')
    source_id = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="ГУИД 1С"
    )

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['name']

    def __str__(self):
        return str(self.name)[:200]


class Department(models.Model):
    """Отдел"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments', verbose_name='Компания')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Родительское подразделение',
        related_name='children'
    )
    name = models.CharField(max_length=255, verbose_name='Название отдела')
    source_id = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="ГУИД 1С"
    )
    job_titles = models.ManyToManyField(
        JobTitle, 
        verbose_name='Должности', 
        related_name='departments_of_job_title', 
        blank=True
    )

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'
        ordering = ['name']

    def __str__(self):
        return self.name







