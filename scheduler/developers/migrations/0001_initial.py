# Generated by Django 4.2.3 on 2023-07-26 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0002_alter_user_last_ready_signal'),
    ]

    operations = [
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('docker_container', models.URLField()),
                ('active', models.BooleanField(default=False)),
                ('developer', models.ForeignKey(limit_choices_to={'is_developer': True}, on_delete=django.db.models.deletion.CASCADE, related_name='services_as_developer', to='profiles.user')),
                ('provider', models.ForeignKey(limit_choices_to={'is_provider': True}, on_delete=django.db.models.deletion.CASCADE, related_name='services_as_provider', to='profiles.user')),
            ],
            options={
                'unique_together': {('name', 'developer')},
            },
        ),
    ]
