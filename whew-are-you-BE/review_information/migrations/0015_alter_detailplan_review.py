# Generated by Django 5.0.7 on 2024-07-29 12:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review_information', '0014_review_likes_review_storage_alter_review_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailplan',
            name='review',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detailplans', to='review_information.review'),
        ),
    ]
