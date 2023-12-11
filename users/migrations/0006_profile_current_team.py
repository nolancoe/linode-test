# Generated by Django 4.2.3 on 2023-07-31 22:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0004_initial'),
        ('users', '0005_delete_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='current_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='teams.team'),
        ),
    ]
