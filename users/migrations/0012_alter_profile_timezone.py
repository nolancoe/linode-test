# Generated by Django 4.2.3 on 2023-08-11 18:26

from django.db import migrations
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_profile_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default='UTC'),
        ),
    ]