# Generated by Django 5.0.7 on 2024-07-28 12:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bingo', '0003_alter_custombingoitem_large_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='bingo_space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='todo', to='bingo.bingospace'),
        ),
    ]
