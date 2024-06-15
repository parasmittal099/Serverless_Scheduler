# Generated by Django 5.0.3 on 2024-04-03 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_alter_user_last_ready_signal'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cpu_efficiency_score',
            field=models.DecimalField(decimal_places=15, max_digits=30, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='memory_efficiency_score',
            field=models.DecimalField(decimal_places=15, max_digits=30, null=True),
        ),
    ]