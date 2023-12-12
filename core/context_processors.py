from django.utils import timezone
from matches.models import Match, DisputeProof, DirectChallenge
from messaging.models import Message

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
    direct_challenge = DirectChallenge.objects.all

    return {'direct_challenge': direct_challenge}


def message_context(request):
    # Get all unread messages associated with the current user
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False)
    return {'unread_messages': unread_messages}