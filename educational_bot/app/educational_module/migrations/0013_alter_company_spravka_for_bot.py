# Generated by Django 4.2.3 on 2024-08-09 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('educational_module', '0012_company_image_test_start_company_spravka_for_bot_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='spravka_for_bot',
            field=models.TextField(blank=True, null=True, verbose_name='Описание бота для справки'),
        ),
    ]