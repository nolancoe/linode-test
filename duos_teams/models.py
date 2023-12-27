from django.db import models
from users.models import Profile
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
import requests
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from PIL import Image, ImageFilter

class DuosTeam(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='team_logos', blank=True, null=True)
    owner = models.ForeignKey(Profile, on_delete=models.SET_NULL, related_name='duos_owned_teams', null=True)
    players = models.ManyToManyField(Profile, related_name='duos_members', blank=True)
    established = models.DateTimeField(default=timezone.now)
    rating = models.FloatField(default=1000)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)

    full_team = models.BooleanField(default=False)
    at_capacity = models.BooleanField(default=False)
    disbanded = models.BooleanField(default=False)

    #Eligibility
    eligible = models.BooleanField(default=False)
    eligible_at = models.DateTimeField(default=now)

    @property
    def formatted_rating(self):
        if self.rating >= 100:
            return "{:.0f}".format(self.rating / 100)
        else:
            return "0"

    def __str__(self):
        return self.name

    def update_team_rating(self):
        # Calculate the average rating of all players on the team
        total_rating = sum(player.rating for player in self.players.all())
        num_players = self.players.count()
        if num_players > 0:
            average_rating = total_rating / num_players
        else:
            average_rating = 0.0  # Handle the case where the team has no players

        # Update the team's rating with the average rating of the players
        self.rating = average_rating
        self.save()

    def save(self, *args, **kwargs):

        if self.id:
            # Update full_team status
            self.at_capacity = self.players.count() >= 4
            self.full_team = self.players.count() >= 2
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

            super().save(*args, **kwargs)

class DuosTeamInvitation(models.Model):
    team = models.ForeignKey(DuosTeam, on_delete=models.CASCADE, related_name='duos_invitations')
    inviting_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='duos_sent_invitations')
    invited_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='duos_received_invitations')
    created_at = models.DateTimeField(default=timezone.now)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation from {self.inviting_user} to {self.invited_user} for team {self.team}"

    class Meta:
        unique_together = ('team', 'invited_user')