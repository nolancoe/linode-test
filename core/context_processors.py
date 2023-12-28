from django.utils import timezone
from matches.models import Match, DisputeProof, DirectChallenge
from messaging.models import Message
from django.shortcuts import redirect
from teams.models import TeamInvitation
from duos_teams.models import DuosTeamInvitation

def matches_context(request):
    matches = Match.objects.all()
    now = timezone.now()
    return {'matches': matches, 'now': now}

def dispute_proofs_context(request):
    # Get all DisputeProof instances associated with the current user
    dispute_proofs = DisputeProof.objects.filter(owner=request.user.id)

    return {'dispute_proofs': dispute_proofs}

def direct_challenge_context(request):
    # Get all DisputeProof instances associated with the current user
    direct_challenges = DirectChallenge.objects.all

    return {'direct_challengs': direct_challenges}


def message_context(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(receiver=request.user, is_read=False)
        return {'unread_messages': unread_messages}
    else:
        return {}


def team_invites_context(request):
    invites = TeamInvitation.objects.all()
    return {'invites' : invites}

def duos_team_invites_context(request):
    duos_invites = DuosTeamInvitation.objects.all()
    return {'duos_invites' : duos_invites}