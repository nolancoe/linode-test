from django.shortcuts import render
from matches.models import Match, DirectChallenge
from django.utils import timezone


def home_view(request):
    matches = Match.objects.all()
    direct_challenges = DirectChallenge.objects.all()
    now = timezone.now()
    return render(request, 'home.html', {'matches': matches, 'now' : now, 'direct_challenges': direct_challenges})