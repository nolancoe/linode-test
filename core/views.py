from django.shortcuts import render
from matches.models import Match, DirectChallenge
from django.utils import timezone
from teams.models import Team



def home_view(request):
    matches = Match.objects.all()
    direct_challenges = DirectChallenge.objects.all()
    now = timezone.now()

    if request.user.is_authenticated:
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
    
    if current_user and current_user.current_duos_team:
        team = current_user.current_duos_team
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

def ladders(request):
    return render(request, 'ladders.html')


def my_teams(request):
    if request.user.is_authenticated:
        current_user = request.user
        check_user_eligibility(current_user)

    return render(request, 'my_teams.html')

def my_challenges_picker(request):
    if request.user.is_authenticated:
        current_user = request.user
        check_user_eligibility(current_user)

    return render(request, 'my_challenges_picker.html')

def disputes_picker(request):
    if request.user.is_authenticated:
        current_user = request.user
        check_user_eligibility(current_user)

    return render(request, 'disputes_picker.html')

def my_matches_picker(request):
    if request.user.is_authenticated:
        current_user = request.user
        check_user_eligibility(current_user)

    return render(request, 'my_matches_picker.html')

def team_invites_picker(request):
    if request.user.is_authenticated:
        current_user = request.user
        check_user_eligibility(current_user)

    return render(request, 'team_invites_picker.html')

def challenges_picker(request):
    if request.user.is_authenticated:
        current_user = request.user
        check_user_eligibility(current_user)

    return render(request, 'challenges_picker.html')

def matches_picker(request):
    if request.user.is_authenticated:
        current_user = request.user
        check_user_eligibility(current_user)

    return render(request, 'matches_picker.html')

def results_picker(request):
    if request.user.is_authenticated:
        current_user = request.user
        check_user_eligibility(current_user)

    return render(request, 'results_picker.html')