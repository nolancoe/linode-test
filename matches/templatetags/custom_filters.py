# custom_filters.py
from django import template
from django.utils import timezone
from pytz import timezone as pytz_timezone
from allauth.socialaccount.models import SocialAccount
from users.models import Profile

register = template.Library()

@register.filter
def convert_to_user_timezone(value, user):
    if user and user.timezone:
        user_tz = pytz_timezone(user.timezone)  # Convert the string to a valid timezone object
        return timezone.localtime(value, timezone=user_tz)
    return value

@register.filter
def get_connected_twitch_players(players):
    connected_players = []

    try:
        if players.exists():
            for player in players:
                try:
                    social_accounts = SocialAccount.objects.filter(user=player)
                    for account in social_accounts:
                        if account.provider == 'twitch':
                            connected_players.append(player)
                except Profile.DoesNotExist:
                    pass
    except AttributeError:
        pass

    return connected_players