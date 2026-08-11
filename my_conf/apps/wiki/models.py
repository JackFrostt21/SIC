from django.db import models


class Project(models.Model):
    title = models.CharField('Название проекта', max_length=200)
    slug = models.SlugField('slug', max_length=200, unique=True)
    description = models.TextField('Описание проекта', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['title']

    def __str__(self):
        return self.title


class Page(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name='Проект', related_name='pages')
    title = models.CharField('Название страницы', max_length=200)
    slug = models.SlugField('slug', max_length=200)
    body = models.TextField('Содержимое страницы', blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, verbose_name='Родительская страница', 
        null=True, blank=True, related_name='children'
        )

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['title']

        constraints = [
            models.UniqueConstraint(fields=['project', 'slug'], name='unique_page_slug_per_project')
        ]

    def __str__(self):
        return self.title