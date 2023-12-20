from django.shortcuts import render
from matches.models import Match, DirectChallenge
from django.utils import timezone


def home_view(request):
    matches = Match.objects.all()
    direct_challenges = DirectChallenge.objects.all()
    now = timezone.now()

    current_user = request.user
    check_user_eligibility(current_user)

    return render(request, 'home.html', {'matches': matches, 'now' : now, 'direct_challenges': direct_challenges})


def check_players_eligibility(current_user):
    if current_user and current_user.current_team:
        team = current_user.current_team
        players = team.players.all()
        
        for player in players:
            if player.eligible_at < timezone.now():
                player.eligible = True
                player.save()

def check_user_eligibility(current_user):
    if current_user:
        if current_user.eligible_at < timezone.now():
            current_user.eligible = True
            current_user.save()