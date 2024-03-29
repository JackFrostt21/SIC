# Generated by Django 4.2.9 on 2024-02-20 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Applications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_fio', models.CharField(max_length=100, null=True)),
                ('user_eriell', models.CharField(max_length=100, null=True)),
                ('name_services', models.CharField(max_length=100, null=True)),
                ('building', models.CharField(max_length=100, null=True)),
                ('floor', models.CharField(max_length=100, null=True)),
                ('block', models.CharField(max_length=100, null=True)),
                ('office_workplace', models.CharField(max_length=100, null=True)),
                ('internal_number', models.CharField(max_length=100, null=True)),
                ('mobile_phone', models.CharField(max_length=100, null=True)),
                ('application_text', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BlockEriell',
            fields=[
                ('id_servises_block', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('number_block', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BuildingEriell',
            fields=[
                ('id_servises_building', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('adress_building', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DirectoryServices',
            fields=[
                ('id_servises_dir_serv', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name_services', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FloorEriell',
            fields=[
                ('id_servises_floor', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('number_floor', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_eriell', models.CharField(max_length=100, null=True)),
                ('email', models.EmailField(max_length=100)),
                ('number_user_telegram', models.CharField(max_length=100)),
                ('internal_number', models.CharField(max_length=100, null=True)),
                ('mobile_phone', models.CharField(max_length=100, null=True)),
                ('user_fio', models.CharField(max_length=100, null=True)),
            ],
        ),
    ]
