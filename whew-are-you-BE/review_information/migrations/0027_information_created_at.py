# Generated by Django 5.0.7 on 2024-08-05 09:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review_information', '0026_alter_comment_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='information',
            name='created_at',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
