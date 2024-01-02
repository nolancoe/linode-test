from django.db import models
from duos_teams.models import DuosTeam
import random
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from users.models import Profile
from matches.models import SupportCategory


OBJECTIVE_MAPS = [
    ('Narrows - Capture The Flag', 'Narrows - Capture The Flag'),
    ('Heretic - Capture The Flag', 'Heretic - Capture The Flag'),
    ('The Pit - Capture The Flag', 'The Pit - Capture The Flag'),
    ('Construct - King Of The Hill', 'Construct - King Of The Hill'),
    ('Guardian - Oddball', 'Guardian - Oddball'),
    ('Onslaught - Capture The Flag', 'Onslaught - Capture The Flag'),
]

SLAYER_MAPS = [
    ('Narrows - Slayer', 'Narrows - Slayer'),
    ('Heretic - Slayer', 'Heretic - Slayer'),
    ('The Pit - Slayer', 'The Pit - Slayer'),
    ('Construct - Slayer', 'Construct - Slayer'),
    ('Amplified - Slayer', 'Amplified - Slayer'),
]

SEARCH_MAPS = [
    ('Highrise - Search & Destroy', 'Highrise - Search & Destroy'),
    ('Invasion - Search & Destroy', 'Invasion - Search & Destroy'),
    ('Karachi - Search & Destroy', 'Karachi - Search & Destroy'),
    ('Scrapyard - Search & Destroy', 'Scrapyard - Search & Destroy'),
    ('Skidrow - Search & Destroy', 'Skidrow - Search & Destroy'),
    ('Terminal - Search & Destroy', 'Terminal - Search & Destroy'),
]

HARDPOINT_MAPS = [
    ('Highrise - Hardpoint', 'Highrise - Hardpoint'),
    ('Invasion - Hardpoint', 'Invasion - Hardpoint'),
    ('Karachi - Hardpoint', 'Karachi - Hardpoint'),
    ('Scrapyard - Hardpoint', 'Scrapyard - Hardpoint'),
    ('Terminal - Hardpoint', 'Terminal - Hardpoint'),
]

CONTROL_MAPS = [
    ('Highrise - Control', 'Highrise - Control'),
    ('Invasion - Control', 'Invasion - Control'),
    ('Karachi - Control', 'Karachi - Control'),
    ('Scrapyard - Control', 'Scrapyard - Control'),
    ('Terminal - Control', 'Terminal - Control'),
]

GAME_MAPS = CONTROL_MAPS + HARDPOINT_MAPS + SEARCH_MAPS

class DuosMatch(models.Model):
    team1 = models.ForeignKey(DuosTeam, on_delete=models.CASCADE, related_name='duos_home_matches')
    team2 = models.ForeignKey(DuosTeam, on_delete=models.CASCADE, related_name='duos_away_matches')


    team1_players = models.ManyToManyField(Profile, related_name='duos_selected_for_team1', blank=True)
    team2_players = models.ManyToManyField(Profile, related_name='duos_selected_for_team2', blank=True)

    date = models.DateTimeField()
    team1_result = models.CharField(max_length=10, blank=True, choices=[('', 'Not Available'), ('win', 'Win'), ('loss', 'Loss'), ('draw', 'Draw')])
    team2_result = models.CharField(max_length=10, blank=True, choices=[('', 'Not Available'), ('win', 'Win'), ('loss', 'Loss'), ('draw', 'Draw')])
    match_completed = models.BooleanField(default=False)
    match_disputed = models.BooleanField(default=False)
    dispute_time = models.DateTimeField(null=True, blank=True, default=None)


    MATCH_TYPES = (
        ('duos', 'Duos'),
    )
    match_type = models.CharField(max_length=10, choices=MATCH_TYPES, default='duos')

    search_only = models.BooleanField(default=False)
    controller_only = models.BooleanField(default=False)

    game1 = models.CharField(max_length=50, blank=True, choices=GAME_MAPS)
    game2 = models.CharField(max_length=50, blank=True, choices=GAME_MAPS)
    game3 = models.CharField(max_length=50, blank=True, choices=GAME_MAPS)

    def __str__(self):
        return f"Match {self.id}: {self.team1}({self.team1.formatted_rating}) vs. {self.team2}({self.team2.formatted_rating})"

    def generate_random_maps(self):
        if self.search_only:
            # If search_only is True, generate maps only from SEARCH_MAPS
            random.shuffle(SEARCH_MAPS)
            self.game1 = SEARCH_MAPS[0][0]
            self.game2 = SEARCH_MAPS[1][0]
            self.game3 = SEARCH_MAPS[2][0]
        else:
            # Shuffle all maps from GAME_MAPS
            random.shuffle(GAME_MAPS)

            control_maps = [map_entry[0] for map_entry in GAME_MAPS if map_entry in CONTROL_MAPS]
            hardpoint_maps = [map_entry[0] for map_entry in GAME_MAPS if map_entry in HARDPOINT_MAPS]
            search_maps = [map_entry[0] for map_entry in GAME_MAPS if map_entry in SEARCH_MAPS]


            random.shuffle(control_maps)
            random.shuffle(hardpoint_maps)
            random.shuffle(search_maps)

            # Assign maps to each game in a way that ensures uniqueness
            games = [control_maps.pop(), hardpoint_maps.pop(), search_maps.pop()]
            random.shuffle(games)

            self.game1 = games[0]
            self.game2 = games[1]
            self.game3 = games[2]

    def save(self, *args, **kwargs):
        # Check if it's a new match instance (not updating an existing one)
        if not self.pk:
            # Generate random maps only if they are not already set
            if not self.game1 or not self.game2 or not self.game3:
                self.generate_random_maps()

        super().save(*args, **kwargs)

class DuosChallenge(models.Model):
    team = models.ForeignKey(DuosTeam, on_delete=models.CASCADE, related_name='duos_challenges')
    date_created = models.DateTimeField(default=timezone.now)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    search_only = models.BooleanField(default=False)
    controller_only = models.BooleanField(default=False)
    challenge_players = models.ManyToManyField(Profile, related_name='duos_selected_players', blank=True)

    def __str__(self):
        return f"{self.team} Challenge"

    def accept_duos_challenge(self, team2, selected_players):
        if not self.accepted:
            new_match = DuosMatch.objects.create(team1=self.team, team2=team2, date=self.scheduled_date, search_only=self.search_only, controller_only=self.controller_only)
            new_match.team1_players.set(self.challenge_players.all())
            new_match.team2_players.set(selected_players)
            new_match.save()

            self.accepted = True
            self.save()
            self.delete()

class DuosDirectChallenge(models.Model):
    challenging_team = models.ForeignKey(DuosTeam, on_delete=models.CASCADE, related_name='duos_direct_challenges')
    challenged_team = models.ForeignKey(DuosTeam, on_delete=models.CASCADE, related_name='duos_challenged_direct_challenges')
    date_created = models.DateTimeField(default=timezone.now)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    search_only = models.BooleanField(default=False)
    controller_only = models.BooleanField(default=False)
    challenge_players = models.ManyToManyField(Profile, related_name='duos_selected_direct_players', blank=True)

    def __str__(self):
        return f"Direct Challenge: {self.challenging_team} to {self.challenged_team}"

    def accept_direct_challenge(self, selected_players):
        if not self.accepted:
            new_match = DuosMatch.objects.create(team1=self.challenging_team, team2=self.challenged_team, date=self.scheduled_date, search_only=self.search_only, controller_only=self.controller_only)
            new_match.team1_players.set(self.challenge_players.all())
            new_match.team2_players.set(selected_players)
            new_match.save() 
            
            self.accepted = True
            self.save()
            self.delete()

class DuosMatchResult(models.Model):
    match = models.ForeignKey('DuosMatch', on_delete=models.CASCADE)
    team_owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    team_result = models.CharField(max_length=10, choices=[('', 'Not Available'), ('win', 'Win'), ('loss', 'Loss'), ('draw', 'Draw')])

    class Meta:
        unique_together = ('match', 'team_owner')

class DuosDisputeProof(models.Model):
    match = models.ForeignKey(DuosMatch, on_delete=models.CASCADE)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    claim = models.TextField(blank=True, null=True)
    game1_screenshot = models.ImageField(upload_to='duos_dispute_screenshots/', blank=True, null=True)
    game2_screenshot = models.ImageField(upload_to='duos_dispute_screenshots/', blank=True, null=True)
    game3_screenshot = models.ImageField(upload_to='duos_dispute_screenshots/', blank=True, null=True)
    additional_evidence = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    expire_at = models.DateTimeField(default=timezone.now)
    updated = models.BooleanField(default=False)

    def __str__(self):
        return f"Proof for Match {self.match} from {self.owner}"

class DuosDispute(models.Model):
    match = models.ForeignKey(DuosMatch, on_delete=models.CASCADE)
    team1_owner_proof = models.OneToOneField(DuosDisputeProof, on_delete=models.CASCADE, related_name='duos_team1_owner_dispute', null=True)
    team2_owner_proof = models.OneToOneField(DuosDisputeProof, on_delete=models.CASCADE, related_name='duos_team2_owner_dispute', null=True)
    created_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Dispute for Match {self.match} between {self.match.team1.owner} and {self.match.team2.owner}"

class DuosMatchSupport(models.Model):
    match = models.ForeignKey(DuosMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    additional_evidence = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    
    def __str__(self):
        return f"Support request for {self.match} from {self.player}"

