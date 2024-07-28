# Generated by Django 5.0.7 on 2024-07-24 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('typetest', '0003_alter_type_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='type',
            name='user',
        ),
        migrations.AddField(
            model_name='type',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='type',
            name='user_type',
            field=models.CharField(choices=[('SQUIRREL', '다람쥐'), ('RABBIT', '토끼'), ('PANDA', '판다'), ('BEAVER', '비버'), ('EAGLE', '독수리'), ('BEAR', '곰'), ('DOLPHIN', '돌고래')], max_length=20),
        ),
    ]