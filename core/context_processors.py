from django.utils import timezone
from matches.models import Match, DisputeProof, DirectChallenge
from messaging.models import Message
from django.shortcuts import redirect
from teams.models import TeamInvitation
from duos_teams.models import DuosTeamInvitation
from duos_matches.models import DuosMatch, DuosDirectChallenge, DuosDisputeProof

def matches_context(request):
    matches = Match.objects.all()
    now = timezone.now()
    return {'matches': matches, 'now': now}

def duos_matches_context(request):
    duos_matches = DuosMatch.objects.all()
    now = timezone.now()
    return {'duos_matches': duos_matches, 'now': now}

def dispute_proofs_context(request):
    # Get all DisputeProof instances associated with the current user
    dispute_proofs = DisputeProof.objects.filter(owner=request.user.id)

    return {'dispute_proofs': dispute_proofs}

def duos_dispute_proofs_context(request):
    # Get all DisputeProof instances associated with the current user
    duos_dispute_proofs = DuosDisputeProof.objects.filter(owner=request.user.id)

    return {'duos_dispute_proofs': duos_dispute_proofs}

def direct_challenge_context(request):
    # Get all DisputeProof instances associated with the current user
    direct_challenges = DirectChallenge.objects.all

    return {'direct_challenges': direct_challenges}

def direct_duos_challenge_context(request):
    # Get all DisputeProof instances associated with the current user
    direct_duos_challenges = DuosDirectChallenge.objects.all()

    return {'direct_duos_challenges': direct_duos_challenges}


def message_context(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(receiver=request.user, is_read=False)
        return {'unread_messages': unread_messages}
    else:
        return {}


def team_invites_context(request):
    if request.user.is_authenticated:
        invites = TeamInvitation.objects.filter(invited_user=request.user)
        return {'invites' : invites}
    else:
        return {}

def duos_team_invites_context(request):
    if request.user.is_authenticated:
        duos_invites = DuosTeamInvitation.objects.filter(invited_user=request.user)
        return {'duos_invites' : duos_invites}
    else:
        return {}