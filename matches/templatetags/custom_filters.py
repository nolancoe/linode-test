# custom_filters.py
from django import template
from django.utils import timezone
from pytz import timezone as pytz_timezone
from allauth.socialaccount.models import SocialAccount
from users.models import Profile
from django.apps import apps


register = template.Library()

@register.filter
def convert_to_user_timezone(value, user):
    if user and user.timezone:
        user_tz = pytz_timezone(user.timezone)  # Convert the string to a valid timezone object
        return timezone.localtime(value, timezone=user_tz)
    return value

@register.filter
def get_connected_twitch_accounts(players):
    twitch_accounts = {}

    try:
        if players.exists():
            for player in players:
                try:
                    social_accounts = SocialAccount.objects.filter(user=player, provider='twitch')
                    if social_accounts.exists():
                        twitch_accounts[player] = social_accounts.first().extra_data.get('login')
                except Profile.DoesNotExist:
                    pass
    except AttributeError:
        pass

    return twitch_accounts
