# Generated by Django 4.2.3 on 2024-10-09 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0011_telegramuser_job_title_alter_telegramuser_is_actual_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramgroup',
            name='lightning_group',
            field=models.BooleanField(default=False, verbose_name='Группа для молний'),
        ),
    ]