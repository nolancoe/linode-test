# Generated by Django 4.2.3 on 2023-08-05 15:20

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('matches', '0007_alter_disputechallenger_additional_evidence_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DisputeChallenger',
            new_name='DisputeProof',
        ),
        migrations.RenameField(
            model_name='dispute',
            old_name='challenger_additional_evidence',
            new_name='team1_additional_evidence',
        ),
        migrations.RenameField(
            model_name='dispute',
            old_name='challenger_claim',
            new_name='team1_claim',
        ),
        migrations.RenameField(
            model_name='dispute',
            old_name='challenger',
            new_name='team1_owner',
        ),
        migrations.RenameField(
            model_name='dispute',
            old_name='challenger_screenshot',
            new_name='team1_screenshot',
        ),
        migrations.RenameField(
            model_name='dispute',
            old_name='respondent_additional_evidence',
            new_name='team2_additional_evidence',
        ),
        migrations.RenameField(
            model_name='dispute',
            old_name='respondent_claim',
            new_name='team2_claim',
        ),
        migrations.RenameField(
            model_name='dispute',
            old_name='respondent',
            new_name='team2_owner',
        ),
        migrations.RenameField(
            model_name='dispute',
            old_name='respondent_screenshot',
            new_name='team2_screenshot',
        ),
        migrations.DeleteModel(
            name='DisputeRespondent',
        ),
    ]