# Generated by Django 5.1.6 on 2025-05-27 21:25

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('english', '0002_alter_englishwords_last_check_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='englishwords',
            name='added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
