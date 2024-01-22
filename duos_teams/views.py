from django.shortcuts import render, redirect, get_object_or_404
from .forms import DuosTeamCreationForm, DuosTeamInvitationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import DuosTeamInvitation, DuosTeam
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from users.models import Profile, Badge
from django.contrib import messages
from pathlib import Path
from django.core.files import File
from django.conf import settings
from users.views import check_email_verification
from core.views import check_players_eligibility
from duos_matches.models import DuosMatch

def user_already_a_player(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.current_duos_team:
            return redirect('already_a_player')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@user_already_a_player
def create_duos_team(request):

    
    is_verified = check_email_verification(request.user)

    if is_verified:
        if request.method == 'POST':
            form = DuosTeamCreationForm(request.POST, request.FILES)
            if form.is_valid():
                team = form.save(commit=False)
                team.owner = request.user  # Set the owner to the currently logged-in user
                team.save()
                form.save_m2m()  # Save the many-to-many relationships (players in this case)
                team.players.add(request.user)  # Add the owner as a player
                team.update_team_rating()
                reset_team_eligibility(team)
                # Update the current_team field of the user's Profile instance
                profile = request.user
                reset_player_eligibility(profile)
                profile.current_duos_team = team
                profile.save()

                return redirect('home')
        else:
            form = DuosTeamCreationForm()
        return render(request, 'create_duos_team.html', {'form': form})
    else:
        return redirect('request_verification')

def already_a_player(request):
    return render(request, 'already_a_player.html')


def duos_team_ladder(request):
    active_teams = DuosTeam.objects.filter(disbanded=False).order_by('-rating')
    return render(request, 'duos_team_ladder.html', {'active_teams': active_teams})


@login_required
def edit_duos_team(request, team_id):
    
    team = get_object_or_404(DuosTeam, id=team_id)

    # Call team eligibility check
    check_team_eligibility(team)

    current_user = request.user
    check_players_eligibility(current_user)

    # Check if the current user is the owner of the team
    if request.user != team.owner:
        return redirect('home')  # Redirect to a home page or an error page if unauthorized

    if request.method == 'POST':
        form = DuosTeamCreationForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            updated_team = form.save(commit=False)
            if not form.cleaned_data['logo']:  # If the logo is cleared
                # Set the default logo
                default_logo_path = Path(settings.MEDIA_ROOT) / 'sweatygameslogo1.png'
                with open(default_logo_path, 'rb') as file:
                    updated_team.logo.save('sweatygameslogo1.png', File(file))
            updated_team.save()
            return redirect('duos_team_detail', team_id=updated_team.id)
    else:
        form = DuosTeamCreationForm(instance=team)

    return render(request, 'edit_duos_team.html', {'form': form, 'team': team})


@login_required
def send_duos_invitation(request, team_id):
    team = get_object_or_404(DuosTeam, id=team_id)

    # Ensure the user sending the invitation is the owner of the team
    if request.user != team.owner:
        return redirect('home')  # Redirect to a home page or an error page if unauthorized

    if team.at_capacity:
        return redirect('home')

    if request.method == 'POST':
        form = DuosTeamInvitationForm(request.POST)
        if form.is_valid():
            invited_user = form.cleaned_data['invited_user']

            # Check if the invited user is already a member of the team
            if invited_user in team.players.all():
                # Redirect to a page informing the user that the invited user is already a team member
                return redirect('user_is_duos_teammate')

            # Check if an invitation already exists for the same team and invited user
            existing_invitation = DuosTeamInvitation.objects.filter(team=team, invited_user=invited_user).first()
            if existing_invitation:
                # Redirect to a page informing the user that an invitation already exists
                return redirect('duos_invitation_already_sent')

            # Create and save the new invitation
            invitation = DuosTeamInvitation(team=team, inviting_user=request.user, invited_user=invited_user)
            invitation.save()

            # Redirect to a success page or the team detail page
            return redirect('duos_invitation_sent')

    else:
        form = DuosTeamInvitationForm()

    return render(request, 'send_duos_invitation.html', {'team': team, 'form': form})


@login_required
def accept_duos_invitation(request, invitation_id):
    invitation = get_object_or_404(DuosTeamInvitation, id=invitation_id)

    # Call team eligibility check
    reset_player_eligibility(invitation.invited_user)

    # Ensure the user can only accept invitations sent to them
    if request.user != invitation.invited_user:
        return redirect('home')  # Redirect to a home page or an error page if unauthorized

    if invitation.team.at_capacity:
        invitation.delete()
        return redirect('home')

    # Mark the invitation as accepted and update the user's current_team field
    if not invitation.is_accepted:
        invitation.is_accepted = True
        invitation.invited_user.current_duos_team = invitation.team
        invitation.invited_user.save()
        invitation.save()

        # Add the user to the list of players on the team
        invitation.team.players.add(request.user)

        # Save the team
        invitation.team.save()

        #award J up badge
        badge_id_to_grant = 13
        badge = Badge.objects.get(id=badge_id_to_grant)
        request.user.badges.add(badge)

        # Update the team's rating with the average rating of the players
        invitation.team.update_team_rating()

        # Delete the invitation after it has been accepted
        invitation.delete()
    return redirect('home')  # Redirect to the desired page after accepting the invitation

def deny_duos_invitation(request, invitation_id):
    invitation = get_object_or_404(DuosTeamInvitation, id=invitation_id)

    if request.user != invitation.invited_user:
        return redirect('home')  # Redirect to a home page or an error page if unauthorized
    
    invitation.delete()
    return redirect('pending_duos_team_invites')


def pending_duos_team_invites(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if the user is not logged in
        
    # Get all the pending invitations for the currently logged-in user
    pending_duos_team_invites = DuosTeamInvitation.objects.filter(invited_user=request.user, is_accepted=False)


    is_verified = check_email_verification(request.user)

    if is_verified:
        if request.method == 'POST':
            # Handle form submission when user accepts or denies an invitation
            invitation_id = request.POST.get('invitation_id')
            action = request.POST.get('action')

            if invitation_id and action:
                invitation = get_object_or_404(DuosTeamInvitation, id=invitation_id)

                if action == 'accept':
                    # Mark the invitation as accepted and update the user's current_team field
                    invitation.is_accepted = True
                    invitation.invited_user.current_duos_team = invitation.team
                    invitation.invited_user.save()
                    invitation.save()
                elif action == 'deny':
                    # Mark the invitation as denied
                    invitation.delete()

                return redirect('pending_duos_team_invites')

        return render(request, 'pending_duos_team_invites.html', {'pending_duos_team_invites': pending_duos_team_invites})
    else:
        return redirect('request_verification')   


def duos_team_detail(request, team_id):
    team = get_object_or_404(DuosTeam, id=team_id)

    past_matches = DuosMatch.objects.filter(
        match_completed=True,
        team1=team  # Filter where the current team is team1
    ) | DuosMatch.objects.filter(
        match_completed=True,
        team2=team  # Filter where the current team is team2
    ).order_by('-date')  # Replace this order_by with your sorting preference

    matches = DuosMatch.objects.filter(
        match_completed=False,
        team1=team  # Filter where the current team is team1
    ) | DuosMatch.objects.filter(
        match_completed=False,
        team2=team  # Filter where the current team is team2
    ).order_by('-date')  # Replace this order_by with your sorting preference

    # Call team eligibility check
    check_team_eligibility(team)

    current_user = request.user
    check_players_eligibility(current_user)

    return render(request, 'duos_team_detail.html', {'team': team, 'past_matches' : past_matches, 'matches' : matches})


@login_required
def remove_player_from_duos_team(request, team_id, player_id):
    # Get the team and player objects
    team = get_object_or_404(DuosTeam, id=team_id)
    player = get_object_or_404(Profile, id=player_id)

    # Ensure the user removing the player is the owner of the team
    if request.user != team.owner:
        return redirect('home')  # Redirect to a home page or an error page if unauthorized

    # Remove the player from the team
    if player in team.players.all():
        team.players.remove(player)

        # Update the team's rating with the average rating of the remaining players
        team.update_team_rating()

        # Set the player's current_team back to None and save the profile
        player.current_duos_team = None
        player.save()

    return redirect('duos_team_detail', team_id=team.id)


@login_required
def leave_duos_team(request, team_id):
    # Get the team object
    team = get_object_or_404(DuosTeam, id=team_id)

    # Ensure the user is a member of the team before they can leave it
    if request.user not in team.players.all():
        return redirect('home')  # Redirect to a home page or an error page if unauthorized

    # Remove the player from the team
    team.players.remove(request.user)

    # Update the team's rating with the average rating of the remaining players
    team.update_team_rating()

    # Set the player's current_team back to None and save the profile
    request.user.current_duos_team = None
    request.user.save()

    return redirect('home')  # Redirect to the desired page after leaving the team

@login_required
def disband_duos_team(request, team_id):
    team = get_object_or_404(DuosTeam, id=team_id)

    # Ensure the user disbanding the team is the owner
    if request.user != team.owner:
        return redirect('home')  # Redirect to a home page or an error page if unauthorized

    # Update the team's name to include disbandment information
    disbandment_date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    new_name = f"{team.name} (Disbanded)"
    team.name = new_name
    team.owner = None
    team.disbanded = True
    team.full_team = False
    team.at_capacity = False
    team.save()

    # Remove all players from the disbanded team and update their profiles
    for player in team.players.all():
        player.current_duos_team = None
        player.save()
    team.players.clear()

    return redirect('home')  # Redirect to the desired page after disbanding the team



def transfer_duos_ownership(request, team_id, new_owner_id):
    team = get_object_or_404(DuosTeam, id=team_id)
    new_owner = get_object_or_404(Profile, id=new_owner_id)
    
    # Check if the current user is the owner of the team
    if request.user == team.owner:
        # Update the team's owner to the new owner
        team.owner = new_owner
        team.save()

        messages.success(request, f"Ownership of {team.name} has been transferred to {new_owner.username}.")
    else:
        messages.error(request, "You do not have permission to transfer ownership.")

    return redirect('duos_team_detail', team_id=team_id)


def user_is_duos_teammate(request):
    return render(request, 'user_is_duos_teammate.html')

def duos_invitation_already_sent(request):
    return render(request, 'duos_invitation_already_sent.html')

def duos_invitation_sent(request):
    return render(request, 'duos_invitation_sent.html')

def reset_team_eligibility(team):
    if team:
        team.eligible = False
        team.eligible_at = timezone.now() + timezone.timedelta(hours=3)
        team.save()

def check_team_eligibility(team):
    if team:
        if team.eligible_at < timezone.now() and team.full_team:
           team.eligible = True
           team.save()

def reset_player_eligibility(profile):
    if profile:
        profile.eligible = False
        profile.eligible_at = timezone.now() + timezone.timedelta(hours=3)
        profile.save()
