from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from .models import Profile

@receiver(user_signed_up, sender=SocialAccount)
def link_steam_account(sender, request, user, **kwargs):
    if kwargs['sociallogin'].account.provider == 'steam':
        # Get Steam account information from SocialAccount
        steam_account = kwargs['sociallogin'].account
        steam_id = steam_account.uid
        steam_username = steam_account.extra_data.get('personaname')
        steam_avatar = steam_account.extra_data.get('avatarfull')

        # Link Steam account to the user's Profile model
        profile, created = Profile.objects.get_or_create(user=user)
        profile.steam_id = steam_id
        profile.steam_username = steam_username
        profile.steam_avatar = steam_avatar
        profile.save()