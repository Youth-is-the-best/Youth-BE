# Generated by Django 5.0.7 on 2024-07-27 15:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('typetest', '0004_remove_type_user_type_content_alter_type_user_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bingo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.IntegerField(default=9)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('change_chance', models.IntegerField(default=3)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomBingoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('large_category', models.CharField(choices=[('CAREER', '채용'), ('CERTIFICATE', '자격증'), ('OUTBOUND', '대외활동'), ('CONTEST', '공모전'), ('SELFCARE', '취미/여행/자기계발/휴식')], max_length=20)),
                ('small_category', models.CharField(blank=True, max_length=20, null=True)),
                ('duty', models.CharField(max_length=50, null=True)),
                ('employment_form', models.CharField(max_length=50, null=True)),
                ('area', models.CharField(max_length=50, null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('host', models.CharField(max_length=50, null=True)),
                ('app_fee', models.IntegerField(null=True)),
                ('prep_period', models.IntegerField(null=True)),
                ('app_due', models.DateField(null=True)),
                ('field', models.CharField(max_length=20, null=True)),
                ('image', models.ImageField(null=True, upload_to='')),
                ('is_editable', models.BooleanField(default=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProvidedBingoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('large_category', models.CharField(choices=[('CAREER', '채용'), ('CERTIFICATE', '자격증'), ('OUTBOUND', '대외활동'), ('CONTEST', '공모전'), ('SELFCARE', '취미/여행/자기계발/휴식')], max_length=20)),
                ('small_category', models.CharField(blank=True, max_length=20, null=True)),
                ('duty', models.CharField(max_length=50, null=True)),
                ('employment_form', models.CharField(max_length=50, null=True)),
                ('area', models.CharField(max_length=50, null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('host', models.CharField(max_length=50, null=True)),
                ('app_fee', models.IntegerField(null=True)),
                ('prep_period', models.IntegerField(null=True)),
                ('app_due', models.DateField(null=True)),
                ('field', models.CharField(max_length=20, null=True)),
                ('image', models.ImageField(null=True, upload_to='')),
                ('is_editable', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='typetest.type')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BingoSpace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_executed', models.BooleanField(default=False)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('location', models.IntegerField()),
                ('bingo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingo.bingo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('self_content', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bingo.custombingoitem')),
                ('recommend_content', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bingo.providedbingoitem')),
            ],
        ),
        migrations.CreateModel(
            name='ToDo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('is_completed', models.BooleanField(default=False)),
                ('bingo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingo.bingo')),
                ('bingo_space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bingo.bingospace')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
