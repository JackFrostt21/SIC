# Generated by Django 4.2.3 on 2024-06-18 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educational_module', '0009_coursetopic_main_text_readuser_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='image_list_settings',
            field=models.ImageField(blank=True, null=True, upload_to='list_settings', verbose_name='image list settings'),
        ),
        migrations.AddField(
            model_name='company',
            name='image_progress',
            field=models.ImageField(blank=True, null=True, upload_to='image_progress', verbose_name='image_progress'),
        ),
    ]