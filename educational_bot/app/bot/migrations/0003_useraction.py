# Generated by Django 4.2.3 on 2024-04-25 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(blank=True, max_length=100, null=True, verbose_name='User')),
                ('action_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='Type of Action')),
                ('action_details', models.TextField(blank=True, null=True, verbose_name='Action Details')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('action_text', models.TextField(blank=True, null=True, verbose_name='Action Text')),
            ],
            options={
                'verbose_name': 'User Action',
                'verbose_name_plural': 'User Actions',
                'ordering': ['-timestamp'],
            },
        ),
    ]