# Generated by Django 5.1.1 on 2024-10-08 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0010_event_device'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='device',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
