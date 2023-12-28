# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import DuosChallenge, DuosMatch, DuosMatchResult, DuosDisputeProof, DuosDispute, DuosDirectChallenge, DuosTeam
from matches.models import Match, Challenge, Team, DirectChallenge
from users.models import Badge, Profile
from .forms import DuosChallengeForm, DuosMatchResultForm, DuosDisputeProofForm, DuosDirectChallengeForm, DuosMatchSupportForm, DuosPlayerSelectionForm
from django.utils import timezone
from matches.glicko2 import update_ratings, process_match_result
from django.db.models import Q
from django.db import transaction
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect
import pprint

from teams.views import check_team_eligibility, reset_team_eligibility
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from core.views import check_players_eligibility, check_user_eligibility



def is_admin(user):
    return user.is_superuser


#check for scheduling conflicts with any matches or challenges
def check_conflicts(selected_players, scheduled_date_user_timezone):
    # Check if the scheduled date conflicts with the user's own scheduled matches
    conflicting_matches = Match.objects.filter(
        Q(team1_players__in=selected_players) | Q(team2_players__in=selected_players),
        date__gte=scheduled_date_user_timezone - timezone.timedelta(hours=1),
        date__lte=scheduled_date_user_timezone
    )

    # Check if the scheduled date conflicts with the user's own scheduled duos matches
    conflicting_duos_matches = DuosMatch.objects.filter(
        Q(team1_players__in=selected_players) | Q(team2_players__in=selected_players),
        date__gte=scheduled_date_user_timezone - timezone.timedelta(hours=1),
        date__lte=scheduled_date_user_timezone
    )
    
    # Check if the scheduled date conflicts with the user's own open challenges
    conflicting_challenges = Challenge.objects.filter(
        challenge_players__in=selected_players,
        scheduled_date__gte=scheduled_date_user_timezone - timezone.timedelta(hours=1),
        scheduled_date__lte=scheduled_date_user_timezone
    )

    # Check if the scheduled date conflicts with the user's own open challenges
    conflicting_duos_challenges = DuosChallenge.objects.filter(
        challenge_players__in=selected_players,
        scheduled_date__gte=scheduled_date_user_timezone - timezone.timedelta(hours=1),
        scheduled_date__lte=scheduled_date_user_timezone
    )

    # Check if the scheduled date conflicts with the user's own Direct challenges
    conflicting_direct_challenges = DirectChallenge.objects.filter(
        challenge_players__in=selected_players,
        scheduled_date__gte=scheduled_date_user_timezone - timezone.timedelta(hours=1),
        scheduled_date__lte=scheduled_date_user_timezone
    )

    # Check if the scheduled date conflicts with the user's own Direct challenges
    conflicting_duos_direct_challenges = DuosDirectChallenge.objects.filter(
        challenge_players__in=selected_players,
        scheduled_date__gte=scheduled_date_user_timezone - timezone.timedelta(hours=1),
        scheduled_date__lte=scheduled_date_user_timezone
    )

    return conflicting_matches.exists() or conflicting_duos_matches.exists() or conflicting_challenges.exists() or conflicting_duos_challenges.exists()

#check for active disputes for any of the users teams
def check_disputes(request, team):
    disputed_match = Match.objects.filter(
        Q(team1=request.user.current_team) | Q(team2=request.user.current_team),
        match_disputed = True
    )

    disputed_duos_match = DuosMatch.objects.filter(
        Q(team1=request.user.current_duos_team) | Q(team2=request.user.current_duos_team),
        match_disputed = True
    )

    return disputed_match.exists() or disputed_duos_match.exists()

@login_required
def create_duos_challenge(request):

    team = request.user.current_duos_team
    check_team_eligibility(team)

    current_user = request.user
    check_players_eligibility(current_user)

    

    if request.method == 'POST':
        
        form = DuosChallengeForm(request.POST, team=request.user.current_duos_team)
        form.user = request.user  # Pass the user to the form
        
        if form.is_valid():
            scheduled_date = form.cleaned_data['scheduled_date']
            user_timezone = request.user.timezone

            team = request.user.current_duos_team
            if not team.eligible:
                form.add_error('scheduled_date', "Your team is not currently eligible to play in matches.")
            else:

                # Convert the scheduled date to the user's timezone
                scheduled_date_user_timezone = scheduled_date.astimezone(user_timezone)
                
                # Calculate the time difference in seconds
                time_difference = (scheduled_date_user_timezone - timezone.now()).total_seconds()

                # Check if the scheduled date is at least 20 minutes in the future
                if time_difference < 1200:  # 1200 seconds = 20 minutes
                    form.add_error('scheduled_date', "Scheduled date must be at least 20 minutes in the future.")
                else:

                    selected_players = form.cleaned_data['challenge_players']

                    has_conflicts = check_conflicts(selected_players, scheduled_date_user_timezone)
                    has_disputes = check_disputes(request, team)
                    

                    if has_disputes:
                        form.add_error(None, "Cannot create a challenge while previous matches are still disputed.")
                    elif has_conflicts:
                        form.add_error('scheduled_date', "Cannot create a challenge that falls within an hour of your already scheduled matches or challenges.")
                    else:
                        challenge = form.save(commit=False)
                        challenge.team = request.user.current_duos_team
                        challenge.scheduled_date = scheduled_date_user_timezone

                        selected_players = form.cleaned_data['challenge_players']

                        # Save the challenge instance to generate an ID
                        challenge.save()

                        # Set the many-to-many relationship after the challenge has an ID
                        challenge.challenge_players.set(selected_players)
                        challenge.save()

                        badge_id = 15
                        has_badge = request.user.badges.filter(id=badge_id).exists()

                        if not has_badge:
                            badge = Badge.objects.get(id=badge_id)  # Get the badge you want to assign
                            request.user.badges.add(badge)  # Assign the badge to the user

                        return redirect('challenges')   
    else:
        form = DuosChallengeForm(team=request.user.current_duos_team)
    return render(request, 'create_duos_challenge.html', {'form': form})



# View for creating a direct challenge
@login_required
def create_direct_duos_challenge(request, team_id):

    team = get_object_or_404(DuosTeam, id=team_id)
    check_team_eligibility(team)

    current_user = request.user
    check_players_eligibility(current_user)


    if request.method == 'POST':
        form = DuosDirectChallengeForm(request.POST, user=request.user)
        form.request = request
        form.user = request.user  # Pass the user to the form

        if form.is_valid():
            scheduled_date = form.cleaned_data['scheduled_date']
            user_timezone = request.user.timezone


            team = request.user.current_duos_team
            if not team.eligible:
                form.add_error('scheduled_date', "Your team is not currently eligible to play in matches.")
            else:

                # Convert the scheduled date to the user's timezone
                scheduled_date_user_timezone = scheduled_date.astimezone(user_timezone)

                # Calculate the time difference in seconds
                time_difference = (scheduled_date_user_timezone - timezone.now()).total_seconds()

                # Check if the scheduled date is at least 20 minutes in the future
                if time_difference < 1200:  # 1200 seconds = 20 minutes
                    form.add_error('scheduled_date', "Scheduled date must be at least 20 minutes in the future.")
                else:
                    selected_players = form.cleaned_data['challenge_players']

                    has_conflicts = check_conflicts(selected_players, scheduled_date_user_timezone)
                    has_disputes = check_disputes(request, team)
                    
                    if has_disputes:
                        form.add_error(None, "Cannot create a challenge while previous matches are still disputed.")
                    elif has_conflicts:
                        form.add_error('scheduled_date', "Cannot create a challenge that falls within an hour of your already scheduled matches or challenges.")
                    else:
                        challenge = form.save(commit=False)
                        challenge.challenging_team = request.user.current_duos_team  # Assuming field name as 'challenging_team'
                        challenge.challenged_team = DuosTeam.objects.get(id=team_id)
                        challenge.scheduled_date = scheduled_date_user_timezone


                        with transaction.atomic():
                            challenge.save()
                            selected_players = form.cleaned_data['challenge_players']
                            challenge.challenge_players.set(selected_players)

                            

                        badge_id = 16
                        has_badge = request.user.badges.filter(id=badge_id).exists()

                        if not has_badge:
                            badge = Badge.objects.get(id=badge_id)  # Get the badge you want to assign
                            request.user.badges.add(badge)  # Assign the badge to the user


                        return redirect('my_challenges')

    else:
        form = DirectChallengeForm(user=request.user)

    challenged_team = DuosTeam.objects.get(id=team_id)
    available_teams = DuosTeam.objects.filter(full_team=True, disbanded=False).exclude(id=request.user.current_team.id)
    context = {
        'form': form,
        'challenged_team': challenged_team,
        'available_teams': available_teams,
    }
    return render(request, 'create_direct_duos_challenge.html', context)


def accept_duos_challenge(request, challenge_id):
    challenge = get_object_or_404(DuosChallenge, pk=challenge_id)

    team = request.user.current_duos_team
    if not team.eligible:
        return redirect('team_not_eligible')
    else:

        # Check if the challenge is within 15 minutes of its scheduled date
        fifteen_minutes_before = timezone.now() + timezone.timedelta(minutes=15)
        if challenge.scheduled_date <= fifteen_minutes_before:
            # If the challenge is within 15 minutes, delete it
            challenge.delete()
            return HttpResponse("Challenge has been deleted as it's within 15 minutes of its scheduled date.", status=410)
        
        if request.user.current_duos_team.full_team and request.user == request.user.current_duos_team.owner and not challenge.accepted:
            team2 = request.user.current_duos_team
            
            proposed_scheduled_date = challenge.scheduled_date

            # Check if there is a match between the teams in the past 12 hours
            past_12_hours = timezone.now() - timezone.timedelta(hours=12)
            previous_match = Match.objects.filter(
                Q(team1=challenge.team, team2=team2) | Q(team1=team2, team2=challenge.team),
                date__gte=past_12_hours
            ).exists()
            
            previous_duos_match = DuosMatch.objects.filter(
                Q(team1=challenge.team, team2=team2) | Q(team1=team2, team2=challenge.team),
                date__gte=past_12_hours
            ).exists()

            if previous_match:
                return redirect('match_farming')

            if previous_duos_match:
                return redirect('match_farming')

            selected_players = form.cleaned_data['challenge_players']

            has_conflicts = check_conflicts(selected_players, scheduled_date_user_timezone)
            has_disputes = check_disputes(request, team)

                    
            if has_disputes:
                return redirect('dispute_conflict')

            if has_conflicts:
                return redirect('schedule_conflict')
            


            if request.method == 'POST':
                form = DuosPlayerSelectionForm(request.POST, team_players=team.players.all())

                if form.is_valid():
                    selected_players = form.cleaned_data['challenge_players']

                    challenge.accept_duos_challenge(team2, selected_players)
                    # Get the newly created match for this challenge
                    match = DuosMatch.objects.filter(
                        Q(team1=challenge.team, team2=team2) | Q(team1=team2, team2=challenge.team)
                    ).latest('date')

                    badge_id = 21
                    has_badge = request.user.badges.filter(id=badge_id).exists()

                    if not has_badge:
                        badge = Badge.objects.get(id=badge_id)
                        request.user.badges.add(badge)

                    return redirect('duos_match_details', match_id=match.id)
                else:
                    # Form is invalid, render the dedicated template for accepting challenge
                    return render(request, 'accept_duos_challenge.html', {'form': form, 'challenge': challenge})
            else:
                form = DuosPlayerSelectionForm(team_players=team.players.all())

            return render(request, 'accept_duos_challenge.html', {'form': form, 'challenge': challenge})


def accept_direct_duos_challenge(request, direct_challenge_id):
    direct_challenge = get_object_or_404(DuosDirectChallenge, pk=direct_challenge_id)

    team = request.user.current_duos_team
    if not team.eligible:
        return redirect('team_not_eligible')
    else:

        # Check if the direct challenge is within 15 minutes of its scheduled date
        fifteen_minutes_before = timezone.now() + timezone.timedelta(minutes=15)
        if direct_challenge.scheduled_date <= fifteen_minutes_before:
            # If the challenge is within 15 minutes, delete it
            direct_challenge.delete()
            return HttpResponse("Direct Challenge has been deleted as it's within 15 minutes of its scheduled date.", status=410)
        
        if request.user.current_duos_team.full_team and request.user == request.user.current_duos_team.owner and not direct_challenge.accepted:
            challenging_team = direct_challenge.challenging_team
            challenged_team = direct_challenge.challenged_team
            proposed_scheduled_date = direct_challenge.scheduled_date

            # Check if there is a match between the teams in the past 12 hours
            past_12_hours = timezone.now() - timezone.timedelta(hours=12)
            
            previous_match = Match.objects.filter(
                Q(team1=challenge.team, team2=team2) | Q(team1=team2, team2=challenge.team),
                date__gte=past_12_hours
            ).exists()
            
            previous_duos_match = DuosMatch.objects.filter(
                Q(team1=challenge.team, team2=team2) | Q(team1=team2, team2=challenge.team),
                date__gte=past_12_hours
            ).exists()

            if previous_match:
                return redirect('match_farming')

            if previous_duos_match:
                return redirect('match_farming')

            selected_profiles = form.cleaned_data['challenge_players']

            has_conflicts = check_conflicts(selected_profiles, scheduled_date_user_timezone)
            has_disputes = check_disputes(request, team)
                    
            if has_disputes:
                return redirect('dispute_conflict')

            if has_conflicts:
                return redirect('schedule_conflict')


            if request.method == 'POST':
                form = DuosPlayerSelectionForm(request.POST, team_players=team.players.all())

                if form.is_valid():
                    selected_profiles = form.cleaned_data['challenge_players']

                    direct_challenge.accept_direct_duos_challenge(selected_profiles)
                    # Get the newly created match for this direct challenge
                    match = DuosMatch.objects.filter(
                        Q(team1=challenging_team, team2=challenged_team) | Q(team1=challenged_team, team2=challenging_team)
                    ).latest('date')

                    badge_id = 21
                    has_badge = request.user.badges.filter(id=badge_id).exists()

                    if not has_badge:
                        badge = Badge.objects.get(id=badge_id)
                        request.user.badges.add(badge)

                    return redirect('duos_match_details', match_id=match.id)
                else:
                    # Form is invalid, render the dedicated template for accepting challenge
                    return render(request, 'accept_direct_duos_challenge.html', {'form': form, 'direct_challenge': direct_challenge})
            else:
                form = DuosPlayerSelectionForm(team_players=team.players.all())

            return render(request, 'accept_direct_duos_challenge.html', {'form': form, 'direct_challenge': direct_challenge})


def cancel_duos_challenge(request, challenge_id):
    challenge = get_object_or_404(DuosChallenge, pk=challenge_id)

    # Check if the user is the owner of the team that created the challenge
    if request.user == challenge.team.owner:
        challenge.delete()

    return redirect('duos_challenges')

def cancel_direct_challenge(request, direct_challenge_id):
    direct_challenge = get_object_or_404(DuosDirectChallenge, pk=direct_challenge_id)

    # Check if the user is the owner of the challenging team
    if request.user == direct_challenge.challenging_team.owner:
        direct_challenge.delete()

    return redirect('my_challenges')



@login_required
def duos_challenges(request):

    if request.user.is_authenticated:
        if request.user.current_duos_team:
            team = request.user.current_duos_team
            check_team_eligibility(team)

            current_user = request.user
            check_players_eligibility(current_user)
    

        # Retrieve challenges that are not yet accepted
        challenges = DuosChallenge.objects.filter(accepted=False)
        
        # Filter challenges that are within 15 minutes of their start time
        challenges_to_delete = challenges.filter(
            scheduled_date__lte=timezone.now() + timezone.timedelta(minutes=15)
        )
        
        # Delete the challenges that meet the condition
        challenges_to_delete.delete()
        
        # Retrieve the updated list of challenges after deletion
        updated_challenges = DuosChallenge.objects.filter(accepted=False)

        if request.user.current_duos_team:
            form = DuosPlayerSelectionForm(team_players=request.user.current_duos_team.players.all())
            return render(request, 'duos_challenges.html', {'challenges': updated_challenges, 'form': form})
        
        return render(request, 'duos_challenges.html', {'challenges': updated_challenges})



def duos_match_details(request, match_id):
    match = get_object_or_404(DuosMatch, pk=match_id)
    
    # Check match time and perform necessary actions
    check_result = check_match_time(match_id)
    
    if isinstance(check_result, HttpResponseRedirect):
        # If check_match_time returns a redirect response, return it immediately
        return check_result
    elif not match:
        # Handle the case where the match no longer exists
        return HttpResponseRedirect(reverse('match_not_found'))  # Redirect to a specific error page or URL
    else:
        # Calculate the time difference between the current datetime and the match datetime
        time_difference = timezone.now() - match.date
        
        # Check if the time difference is 15 minutes or more
        is_match_over = time_difference.total_seconds() >= 15 * 60
        return render(request, 'duos_match_details.html', {'match': match, 'is_match_over': is_match_over})








def check_match_time(match_id):
    match = get_object_or_404(DuosMatch, pk=match_id)

    # Check if more than 90 minutes have passed since the match started
    time_difference = timezone.now() - match.date
    if time_difference.total_seconds() > 5400:  # 90 minutes * 60 seconds
        # Check if any match results are submitted for this match
        match_results = DuosMatchResult.objects.filter(match=match)

        if match_results.exists():
            # Get the submitted match result for each team
            team1_result = match_results.filter(team_owner=match.team1.owner).first()
            team2_result = match_results.filter(team_owner=match.team2.owner).first()

            if not match.match_completed:
                if team1_result and not team2_result:
                    # Only team 1 submitted results
                    team1_submitted_result = team1_result.team_result

                    if team1_submitted_result == 'win':
                        match.team1_result = 'win'
                        match.team2_result = 'loss'
                    elif team1_submitted_result == 'loss':
                        match.team1_result = 'loss'
                        match.team2_result = 'win'

                    match.match_completed = True
                    match.save()
                    return HttpResponseRedirect(reverse('duos_match_details', kwargs={'match_id': match_id}))

                elif team2_result and not team1_result:
                    # Only team 2 submitted results
                    team2_submitted_result = team2_result.team_result

                    if team2_submitted_result == 'win':
                        match.team1_result = 'loss'
                        match.team2_result = 'win'
                    elif team2_submitted_result == 'loss':
                        match.team1_result = 'win'
                        match.team2_result = 'loss'

                    match.match_completed = True
                    match.save()
                    return HttpResponseRedirect(reverse('duos_match_details', kwargs={'match_id': match_id}))
        else:
            # No match results submitted, delete the match
            match.delete()
            return HttpResponseRedirect(reverse('home'))