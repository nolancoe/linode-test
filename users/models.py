from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django_countries.fields import CountryField
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from timezone_field import TimeZoneField
from django.utils import timezone


class Badge(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='badge_photos/')
    description = models.TextField()

    def __str__(self):
        return self.name



class Profile(AbstractUser):
    #basic info fields
    bio = models.TextField(max_length=100, blank=True)
    birthday = models.DateField(default=date.today) 
    country = CountryField(default='US')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    timezone = TimeZoneField(default='UTC')
    
    #Social Links
    twitch_link = models.URLField(max_length=255, blank=True, null=True)
    twitter_link = models.URLField(max_length=255, blank=True, null=True)
    youtube_link = models.URLField(max_length=255, blank=True, null=True)
    activision_id = models.CharField(max_length=50, blank=True, null=True)
    gamertag = models.CharField(max_length=15, blank=True, null=True)
    psnid = models.CharField(max_length=16, blank=True, null=True)
    
    #Eligibility
    eligible = models.BooleanField(default=True)
    eligible_at = models.DateTimeField(default=now)

    #team fields
    current_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, blank=True, null=True, related_name='members')
    current_duos_team = models.ForeignKey('duos_teams.DuosTeam', on_delete=models.SET_NULL, blank=True, null=True, related_name='duos_members')

    #Rating System Fields
    rating = models.FloatField(default=1000)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)

    strikes = models.PositiveIntegerField(default=0)

    is_banned = models.BooleanField(default=False)

    #Badges
    badges = models.ManyToManyField(Badge, related_name='users', blank=True)
    
    @property
    def formatted_rating(self):
        if self.rating >= 100:
            return "{:.0f}".format(self.rating / 100)
        else:
            return "0"


    def __str__(self):
        return f"{self.username} ({self.formatted_rating})"


class Report(models.Model):
    reporter = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reports_filed')
    reported_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Report by {self.reporter} against {self.reported_user}"

class BugReport(models.Model):
    reporter = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = models.TextField()
    reported_at = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"Bug ID: {self.pk} - {self.reported_at}"

class Suggestion(models.Model):
    reporter = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = models.TextField()
    reported_at = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"Suggestion ID: {self.pk} - {self.reported_at}"

