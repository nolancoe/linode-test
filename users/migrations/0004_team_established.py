# Generated by Django 4.2.3 on 2023-07-31 22:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_team_name_alter_team_owner_remove_team_players_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='established',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
