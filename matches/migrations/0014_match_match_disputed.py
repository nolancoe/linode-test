# Generated by Django 4.2.3 on 2023-08-15 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0013_disputeproof_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='match_disputed',
            field=models.BooleanField(default=False),
        ),
    ]