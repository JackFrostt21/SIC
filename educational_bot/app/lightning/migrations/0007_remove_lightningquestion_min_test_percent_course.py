# Generated by Django 4.2.3 on 2024-10-20 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lightning', '0006_lightning_min_test_percent_course_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lightningquestion',
            name='min_test_percent_course',
        ),
    ]
