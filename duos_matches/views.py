# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import DuosChallenge, DuosMatch, DuosMatchResult, DuosDisputeProof, DuosDispute, DuosDirectChallenge, DuosTeam, DuosMatchSupport
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
from django.utils.timesince import timesince



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


                        return redirect('my_duos_challenges')

    else:
        form = DuosDirectChallengeForm(user=request.user)

    challenged_team = DuosTeam.objects.get(id=team_id)
    available_teams = DuosTeam.objects.filter(full_team=True, disbanded=False).exclude(id=request.user.current_duos_team.id)
    context = {
        'form': form,
        'challenged_team': challenged_team,
        'available_teams': available_teams,
    }
    return render(request, 'create_direct_duos_challenge.html', context)


def accept_duos_challenge(request, challenge_id):
    challenge = get_object_or_404(DuosChallenge, pk=challenge_id)
    team = request.user.current_duos_team
    user_timezone = request.user.timezone
    scheduled_date_user_timezone = challenge.scheduled_date.astimezone(user_timezone)
    

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
                

            previous_duos_match = DuosMatch.objects.filter(
                Q(team1=challenge.team, team2=team2) | Q(team1=team2, team2=challenge.team),
                date__gte=past_12_hours
            ).exists()

            if previous_duos_match:
                return redirect('match_farming')


            if request.method == 'POST':
                form = DuosPlayerSelectionForm(request.POST, team_players=team.players.all())

                if form.is_valid():
                    scheduled_date_user_timezone = challenge.scheduled_date.astimezone(user_timezone)
                    selected_players = form.cleaned_data['challenge_players']

                    has_conflicts = check_conflicts(selected_players, scheduled_date_user_timezone)
                    has_disputes = check_disputes(request, team)
         
                    if has_disputes:
                        return redirect('dispute_conflict')

                    if has_conflicts:
                        return redirect('schedule_conflict')

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
    user_timezone = request.user.timezone
    scheduled_date_user_timezone = direct_challenge.scheduled_date.astimezone(user_timezone)

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
            
            
            previous_duos_match = DuosMatch.objects.filter(
                Q(team1=team, team2=challenging_team) | Q(team1=challenging_team, team2=team),
                date__gte=past_12_hours
            ).exists()


            if previous_duos_match:
                return redirect('match_farming')

            

            


            if request.method == 'POST':
                form = DuosPlayerSelectionForm(request.POST, team_players=team.players.all())

                if form.is_valid():
                    selected_profiles = form.cleaned_data['challenge_players']


                    has_conflicts = check_conflicts(selected_profiles, scheduled_date_user_timezone)
                    has_disputes = check_disputes(request, team)
                            
                    if has_disputes:
                        return redirect('dispute_conflict')

                    if has_conflicts:
                        return redirect('schedule_conflict')

                    direct_challenge.accept_direct_challenge(selected_profiles)
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

def cancel_direct_duos_challenge(request, direct_challenge_id):
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


def update_duos_wins_and_losses (request, match_id):
    match = get_object_or_404(DuosMatch, pk=match_id)

    if match.team1_result == "win":
        match.team1.wins += 1
        for player in match.team1_players.all():
            player.wins += 1
            player.save()
    elif match.team1_result == "loss":
        match.team1.losses += 1
        for player in match.team1_players.all():
            player.losses += 1
            player.save()
    match.team1.save()

    if match.team2_result == "win":
        match.team2.wins += 1
        for player in match.team2_players.all():
            player.wins += 1
            player.save()
    elif match.team2_result == "loss":
        match.team2.losses += 1
        for player in match.team2_players.all():
            player.losses += 1
            player.save()
    match.team2.save()


def submit_duos_results(request, match_id):
    match = get_object_or_404(DuosMatch, pk=match_id)

    # Check if the match is already completed (both team owners submitted results)
    if match.match_completed:
        return redirect('duos_match_details', match_id=match_id)

    if request.method == 'POST':
        form = DuosMatchResultForm(request.POST)
        if form.is_valid():
            # Save the submitted result to the MatchResult model for the logged-in user
            user_team_result = form.cleaned_data['team_result']
            DuosMatchResult.objects.update_or_create(
                match=match,
                team_owner=request.user,
                defaults={'team_result': user_team_result}
            )
            
            # Check if both team owners have submitted the results
            match_results_count = DuosMatchResult.objects.filter(match=match).count()


            badge_id = 17
            has_badge = request.user.badges.filter(id=badge_id).exists()

            if not has_badge:
                badge = Badge.objects.get(id=badge_id)  # Get the badge you want to assign
                request.user.badges.add(badge)  # Assign the badge to the user


            if match_results_count == 2:
                # Get both team results
                team1_result = DuosMatchResult.objects.get(match=match, team_owner=match.team1.owner).team_result
                team2_result = DuosMatchResult.objects.get(match=match, team_owner=match.team2.owner).team_result
            
                # Check if both team results are different (one reported a win and the other reported a loss)
                if team1_result != team2_result:
                # Update the Match model with the final results
                    match.team1_result = team1_result
                    match.team2_result = team2_result
                    match.match_completed = True
                    match.match_disputed = False
                    match.save()
                    process_match_result(match, team1_result, team2_result, match.team1, match.team2)

                    # Update team ratings for both teams
                    match.team1.update_team_rating()
                    match.team2.update_team_rating()

                    #update wins and losses
                    update_duos_wins_and_losses(request, match_id)

                    # Return a success message or redirect to the match details page
                    return redirect('duos_match_details', match_id=match_id)
                else:
                    now = timezone.now()
                    team1_owner = match.team1.owner
                    team2_owner = match.team2.owner

                    expire_at = now + timezone.timedelta(hours=1)

                    # Create instances of DisputeProof for both team owners
                    DuosDisputeProof.objects.create(match=match, owner=team1_owner, expire_at=expire_at)
                    DuosDisputeProof.objects.create(match=match, owner=team2_owner, expire_at=expire_at)
                    match.match_disputed = True
                    match.dispute_time = timezone.now()
                    match.save()

                    # Redirect team owners to the match details page
                    return redirect('duos_dispute_proofs_list')

                    
        return redirect('submit_results_success')
    else:
        form = DuosMatchResultForm()

    return render(request, 'submit_duos_results.html', {'form': form})



def update_duos_dispute_proof(request, proof_id):
    dispute_proof = get_object_or_404(DuosDisputeProof, pk=proof_id)
    match = dispute_proof.match
    dispute_proof1 = DuosDisputeProof.objects.get(owner=match.team1.owner, match=match)
    dispute_proof2 = DuosDisputeProof.objects.get(owner=match.team2.owner, match=match)

    # Calculate the time difference between now and the created_at time
    time_since_dispute = timezone.now() - dispute_proof.created_at

    if time_since_dispute < timezone.timedelta(hours=1):
        if request.method == 'POST':
            form = DuosDisputeProofForm(request.POST, request.FILES, instance=dispute_proof)
            if form.is_valid():
                form.save()

                # Set the "updated" field to True
                dispute_proof.updated = True
                dispute_proof.save()

                # Check if there is another DisputeProof instance for the match
                other_proof = DuosDisputeProof.objects.filter(match=dispute_proof.match).exclude(owner=dispute_proof.owner).first()

                if other_proof:
                    # Create an instance of the Dispute model only if it doesn't exist
                    dispute, created = DuosDispute.objects.get_or_create(match=dispute_proof.match)

                    # Set team1_owner_proof and team2_owner_proof fields
                    if dispute_proof.owner == match.team1.owner:
                        dispute.team1_owner_proof = dispute_proof
                    else:
                        dispute.team2_owner_proof = dispute_proof

                    # Save the Dispute model
                    dispute.save()

                    # Redirect to the match details page or display a success message
                    return redirect('duos_match_details', match_id=dispute_proof.match.id)
                else:
                    # If there's no other DisputeProof instance, stay on the form page
                    return redirect('update_duos_dispute_proof', proof_id=proof_id)

        else:
            form = DuosDisputeProofForm(instance=dispute_proof)

        return render(request, 'update_duos_dispute_proof.html', {'form': form, 'match': dispute_proof.match})
    else:
        # If it has been an hour or more since created_at time
        other_proof = DuosDisputeProof.objects.filter(match=dispute_proof.match).exclude(owner=dispute_proof.owner).first()

        if other_proof and other_proof.updated:
            # Create a new Dispute instance with other_proof
            dispute, created = DuosDispute.objects.get_or_create(match=dispute_proof.match)

            if dispute_proof.owner == match.team1.owner:
                dispute.team2_owner_proof = other_proof
            else:
                dispute.team1_owner_proof = other_proof

            # Save the Dispute model
            dispute.save()

            # Redirect to the match details page or display a success message
            return redirect('dispute_under_review')

        elif dispute_proof.updated and not other_proof.updated:
            return redirect('dispute_under_review')

        else:
            # If there's no other_proof, delete the match and related objects
            match.delete()

            # Redirect or display appropriate message
            return redirect('dispute_expired')  # You might want to redirect to a different view


def duos_dispute_proofs_list(request):
    # Get all DisputeProof instances associated with the current user


    return render(request, 'duos_dispute_proofs_list.html')

@user_passes_test(is_admin)
def duos_dispute_proof_details(request, proof_id):
    dispute_proof = get_object_or_404(DuosDisputeProof, pk=proof_id)
    return render(request, 'duos_dispute_proof_details.html', {'dispute_proof': dispute_proof})

@user_passes_test(is_admin)
def duos_dispute_details(request, dispute_id):
    dispute = get_object_or_404(DuosDispute, pk=dispute_id)
    match = dispute.match

    if request.method == 'POST':
        # Check if the form is submitted with match results for resolution
        team1_result = request.POST.get('team1_result')
        team2_result = request.POST.get('team2_result')

        # Update the match instance with the resolved results
        match.team1_result = team1_result
        match.team2_result = team2_result
        match.match_completed = True
        match.save()

        # Process match result
        process_match_result(match, team1_result, team2_result, match.team1, match.team2)

        # Update team ratings for both teams
        match.team1.update_team_rating()
        match.team2.update_team_rating()

        # Mark the dispute as resolved
        dispute.resolved = True
        dispute.save()
        
        #update wins and losses
        update_duos_wins_and_losses(request, match.id)
        
        # Get the MatchResult instances for the match
        team1_match_result = DuosMatchResult.objects.get(match=match, team_owner=match.team1.owner)
        team2_match_result = DuosMatchResult.objects.get(match=match, team_owner=match.team2.owner)

        # Determine which team owner to penalize
        if team1_match_result.team_result != team1_result:
            team_owner_to_penalize = match.team1.owner
        elif team2_match_result.team_result != team2_result:
            team_owner_to_penalize = match.team2.owner
        else:
            team_owner_to_penalize = None

        # Increment the strikes field of the corresponding team owner's user profile
        if team_owner_to_penalize:
            with transaction.atomic():
                team_owner_to_penalize.strikes += 1
                team_owner_to_penalize.save()
            if team_owner_to_penalize.strikes == 3:
                    team_owner_to_penalize.is_banned = True
                    team_owner_to_penalize.save()

            reset_team_eligibility(team_owner_to_penalize.current_duos_team)

        # Redirect to the dispute details page with the updated data
        return redirect('duos_dispute_details', dispute_id=dispute_id)

    return render(request, 'duos_dispute_details.html', {'dispute': dispute, 'match': match})

@user_passes_test(is_admin)
def duos_disputes_list(request):
    now = timezone.now()
    disputes = DuosDispute.objects.all()

    return render(request, 'duos_disputes_list.html', {'disputes': disputes, 'now': now})


def duos_match_list(request):
    matches = DuosMatch.objects.filter(
        match_completed=False,
    ).order_by('-date')

    return render(request, 'duos_match_list.html', {'matches': matches,})

def past_duos_match_list(request):
    matches = DuosMatch.objects.filter(
        match_completed=True,
    ).order_by('-date')

    return render(request, 'past_duos_match_list.html', {'matches': matches})

def my_duos_match_list(request):
    matches = DuosMatch.objects.filter(
        Q(team1_players=request.user) | Q(team2_players=request.user),
        match_completed=False,
          # Filter matches where the user is in either team1 or team2
    ).order_by('-date').distinct()

    now = timezone.now()

    # Loop through each match and run the check_match_time function
    for match in matches:
        check_match_time(match.id)

    return render(request, 'my_duos_matches.html', {'matches': matches, 'now' : now})

def my_past_duos_match_list(request):
    user_team = request.user.current_duos_team  # Assuming current_team is a ForeignKey in the Profile model

    # Fetch matches where the current user's team was involved (either as team1 or team2)
    matches = DuosMatch.objects.filter(
        match_completed=True,
        team1=user_team  # Filter where the current team is team1
    ) | DuosMatch.objects.filter(
        match_completed=True,
        team2=user_team  # Filter where the current team is team2
    ).order_by('-date')  # Replace this order_by with your sorting preference

    return render(request, 'my_past_duos_matches.html', {'matches': matches})


@login_required
def my_duos_challenges(request):

    # Assuming the logged-in user is associated with a team
    if request.user.is_authenticated and hasattr(request.user, 'current_duos_team'):
        team = request.user.current_duos_team
        # Call team eligibility check
        check_team_eligibility(team)

        current_user = request.user
        check_players_eligibility(current_user)

         # Retrieve challenges associated with the user's team that are not yet accepted
        my_challenges = DuosChallenge.objects.filter(team=team, accepted=False)

        # Filter challenges that are within 15 minutes of their start time
        challenges_to_delete = my_challenges.filter(
            scheduled_date__lte=timezone.now() + timezone.timedelta(minutes=15)
        )
        
        # Delete the challenges that meet the condition
        challenges_to_delete.delete()
        
        # Retrieve the updated list of challenges after deletion
        updated_challenges = DuosChallenge.objects.filter(team=team, accepted=False)
        
        # Retrieve direct challenges where the user's team is the challenging team
        my_challenging_direct_challenges = DuosDirectChallenge.objects.filter(challenging_team=team)
        
        # Retrieve direct challenges where the user's team is the challenged team
        my_challenged_direct_challenges = DuosDirectChallenge.objects.filter(challenged_team=team)

        # Delete old direct challenges
        my_challenging_direct_challenges_to_delete = my_challenging_direct_challenges.filter(
            scheduled_date__lte=timezone.now() + timezone.timedelta(minutes=15)
        )

        my_challenged_direct_challenges_to_delete = my_challenged_direct_challenges.filter(
            scheduled_date__lte=timezone.now() + timezone.timedelta(minutes=15)
        )
        
        my_challenging_direct_challenges_to_delete.delete()
        my_challenged_direct_challenges_to_delete.delete()



        if request.user.current_duos_team:
            form = DuosPlayerSelectionForm(team_players=request.user.current_duos_team.players.all())
            return render(request, 'my_duos_challenges.html', {'my_challenges': updated_challenges, 'my_challenging_direct_challenges': my_challenging_direct_challenges, 'my_challenged_direct_challenges': my_challenged_direct_challenges, 'form': form})


        return render(
            request,
            'my_challenges.html',
            {
                'my_challenges': updated_challenges,
                'duos_challenges': updated_challenges,
                'challenges': sorted_challenges,
                'my_challenging_direct_challenges': my_challenging_direct_challenges,
                'my_challenged_direct_challenges': my_challenged_direct_challenges,
            }
        )
    else:
        return render(request, 'home.html')



def decline_direct_duos_challenge(request, challenge_id):
    # Retrieve the direct challenge instance
    direct_challenge = get_object_or_404(DuosDirectChallenge, pk=challenge_id)
    
    # Check if the logged-in user is the owner of the challenged team
    if request.user == direct_challenge.challenged_team.owner:
        # Delete the direct challenge
        direct_challenge.delete()
    
    # Redirect to a specific page after declining and deleting the challenge
    return redirect('my_duos_challenges')  # Adjust 'my_challenges' to your desired URL name

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


def request_duos_match_support(request, match_id):
    match = DuosMatch.objects.get(id=match_id)

    if request.user == match.team1.owner or request.user == match.team2.owner:
        if request.method == 'POST':
            form = DuosMatchSupportForm(request.POST)
            if form.is_valid():
                support_request = form.save(commit=False)
                support_request.match = match
                support_request.player = request.user
                support_request.save()
                return redirect('support_request_success')
        else:
            form = DuosMatchSupportForm()

        context = {
            'form': form,
            'match': match,
        }
        return render(request, 'duos_support_request_form.html', context)
    else: 
        return redirect('home')


@user_passes_test(is_admin)
def duos_support_list(request):
    open_support = DuosMatchSupport.objects.filter(status='open')
    closed_support = DuosMatchSupport.objects.filter(status='closed')

    context = {
        'open_support': open_support,
        'closed_support': closed_support,
    }

    return render(request, 'duos_support_list.html', context)

@user_passes_test(is_admin)
def duos_support_detail(request, support_id):
    support = get_object_or_404(DuosMatchSupport, id=support_id)
    return render(request, 'duos_support_detail.html', {'support': support})


@user_passes_test(is_admin)
def change_duos_support_status(request, support_id):
    support = DuosMatchSupport.objects.get(pk=support_id)
    # Update the status to 'Closed'
    support.status = 'closed'
    support.save()
    return redirect('duos_support_detail', support_id=support_id)