# Generated by Django 5.0.7 on 2024-07-31 11:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bingo', '0007_alter_custombingoitem_prep_period_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='providedbingoitem',
            name='is_notice',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('ProvidedBingoItem', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notice', to='bingo.providedbingoitem')),
                ('likes', models.ManyToManyField(blank=True, related_name='like_notice', to=settings.AUTH_USER_MODEL)),
                ('storage', models.ManyToManyField(blank=True, related_name='storage_notice', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
