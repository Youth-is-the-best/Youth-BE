# Generated by Django 5.0.7 on 2024-08-01 17:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bingo', '0011_dday'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dday',
            name='rest_school_dday',
        ),
        migrations.RemoveField(
            model_name='dday',
            name='return_school_dday',
        ),
    ]