# Generated by Django 4.2.3 on 2024-10-08 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_requestlog_is_actual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='is_actual',
            field=models.BooleanField(default=False, verbose_name='Отобразить'),
        ),
    ]
