# Generated by Django 4.2.3 on 2023-12-27 20:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0031_directchallenge_challenge_players'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('duos_matches', '0005_duosdisputeproof'),
    ]

    operations = [
        migrations.CreateModel(
            name='DuosMatchSupport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('additional_evidence', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], default='open', max_length=10)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.supportcategory')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='duos_matches.duosmatch')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DuosDispute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('resolved', models.BooleanField(default=False)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='duos_matches.duosmatch')),
                ('team1_owner_proof', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='duos_team1_owner_dispute', to='duos_matches.duosdisputeproof')),
                ('team2_owner_proof', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='duos_team2_owner_dispute', to='duos_matches.duosdisputeproof')),
            ],
        ),
    ]