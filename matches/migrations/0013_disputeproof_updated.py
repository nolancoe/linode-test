# Generated by Django 4.2.3 on 2023-08-14 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0012_alter_disputeproof_claim'),
    ]

    operations = [
        migrations.AddField(
            model_name='disputeproof',
            name='updated',
            field=models.BooleanField(default=False),
        ),
    ]
