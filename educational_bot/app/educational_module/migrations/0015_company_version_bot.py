# Generated by Django 4.2.3 on 2024-09-09 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educational_module', '0014_alter_coursetopic_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='version_bot',
            field=models.TextField(blank=True, null=True, verbose_name='Версия бота'),
        ),
    ]
