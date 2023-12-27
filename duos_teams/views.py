from django.shortcuts import render, redirect, get_object_or_404
from .forms import TeamCreationForm, TeamInvitationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import TeamInvitation, Team
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from users.models import Profile, Badge
from django.contrib import messages
from pathlib import Path
from django.core.files import File
from django.conf import settings
from users.views import check_email_verification
from core.views import check_players_eligibility


def user_already_a_player(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.current_team:
            return redirect('already_a_player')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
