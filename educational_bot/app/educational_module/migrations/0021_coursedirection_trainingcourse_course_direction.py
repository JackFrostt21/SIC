# Generated by Django 4.2.3 on 2024-09-26 10:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('educational_module', '0020_alter_trainingcourse_group_alter_trainingcourse_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseDirection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='Название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Направление программы обучения',
                'verbose_name_plural': 'Направления программ обучения',
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='trainingcourse',
            name='course_direction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='educational_module.coursedirection', verbose_name='Направление программы обучения'),
        ),
    ]
