# Generated by Django 4.2.3 on 2024-08-06 10:00

import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_alter_telegramgroup_description_and_more'),
        ('educational_module', '0011_company_image_test_failed_company_image_test_passed'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='image_test_start',
            field=models.ImageField(blank=True, null=True, upload_to='start_images', verbose_name='Стартовое изображение для теста'),
        ),
        migrations.AddField(
            model_name='company',
            name='spravka_for_bot',
            field=models.TextField(blank=True, null=True, verbose_name='Справка для бота'),
        ),
        migrations.AlterField(
            model_name='answeroption',
            name='topic_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_options', to='educational_module.topicquestion', verbose_name='вопрос по теме'),
        ),
        migrations.AlterField(
            model_name='company',
            name='color_theme_company',
            field=colorfield.fields.ColorField(default='#4a8bed', image_field=None, max_length=25, samples=None, verbose_name='Основной цвет компании'),
        ),
        migrations.AlterField(
            model_name='company',
            name='image_list_courses',
            field=models.ImageField(blank=True, null=True, upload_to='list_courses', verbose_name='Изображение для списка курсов в ТГ'),
        ),
        migrations.AlterField(
            model_name='company',
            name='image_list_settings',
            field=models.ImageField(blank=True, null=True, upload_to='list_settings', verbose_name='Изображение для настроек в ТГ'),
        ),
        migrations.AlterField(
            model_name='company',
            name='image_progress',
            field=models.ImageField(blank=True, null=True, upload_to='image_progress', verbose_name='Изображение для прогресса в ТГ'),
        ),
        migrations.AlterField(
            model_name='company',
            name='image_start_company',
            field=models.ImageField(blank=True, null=True, upload_to='start_images', verbose_name='Стартовое изображение для ТГ'),
        ),
        migrations.AlterField(
            model_name='company',
            name='image_test_failed',
            field=models.ImageField(blank=True, null=True, upload_to='test failed', verbose_name='Изображение для неудачно пройденного теста'),
        ),
        migrations.AlterField(
            model_name='company',
            name='image_test_passed',
            field=models.ImageField(blank=True, null=True, upload_to='test passed', verbose_name='Изображение для успешно пройденного теста'),
        ),
        migrations.AlterField(
            model_name='company',
            name='logo_company',
            field=models.ImageField(blank=True, null=True, upload_to='company', verbose_name='Логотип компании'),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='coursetopic',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='coursetopic',
            name='image_course_topic',
            field=models.ImageField(blank=True, null=True, upload_to='Course_Topic', verbose_name='Изображение для темы курса'),
        ),
        migrations.AlterField(
            model_name='coursetopic',
            name='main_text_readuser',
            field=models.BooleanField(default=False, verbose_name='Отображать основной текст в ТГ'),
        ),
        migrations.AlterField(
            model_name='coursetopic',
            name='main_text_webapp_readuser',
            field=models.BooleanField(default=False, verbose_name='Отображать основной текст в ТГ в формате WebApp'),
        ),
        migrations.AlterField(
            model_name='coursetopic',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='Course_Topic', verbose_name='PDF файл для курса'),
        ),
        migrations.AlterField(
            model_name='coursetopic',
            name='pdf_file_readuser',
            field=models.BooleanField(default=False, verbose_name='Отображать PDF файл в ТГ'),
        ),
        migrations.AlterField(
            model_name='topicquestion',
            name='training',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='educational_module.trainingcourse', verbose_name='курс'),
        ),
        migrations.AlterField(
            model_name='trainingcourse',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='trainingcourse',
            name='group',
            field=models.ManyToManyField(blank=True, null=True, to='bot.telegramgroup', verbose_name='Группа пользователей'),
        ),
        migrations.AlterField(
            model_name='trainingcourse',
            name='image_course',
            field=models.ImageField(blank=True, null=True, upload_to='training_course', verbose_name='Изображение для курса'),
        ),
        migrations.AlterField(
            model_name='trainingcourse',
            name='min_test_percent_course',
            field=models.IntegerField(default=90, verbose_name='Минимальный процент для прохождения курса'),
        ),
        migrations.AlterField(
            model_name='trainingcourse',
            name='user',
            field=models.ManyToManyField(blank=True, null=True, to='bot.telegramuser', verbose_name='Пользователь'),
        ),
    ]
