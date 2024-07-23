# Generated by Django 5.0.7 on 2024-07-23 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_verif'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='birth',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='college',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='major',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='verif',
            name='hash',
            field=models.CharField(max_length=45, null=True),
        ),
    ]
