# Generated by Django 4.2.3 on 2023-12-17 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0026_match_controller_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='controller_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='directchallenge',
            name='controller_only',
            field=models.BooleanField(default=False),
        ),
    ]
