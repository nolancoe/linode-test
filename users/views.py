# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, ProfileForm, ReportForm, BugReportForm, SuggestionForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate, logout
from social_django.views import auth
from social_django.models import UserSocialAuth
from django.contrib.auth.decorators import login_required
import random
import string
import requests
from django.http import HttpResponse, JsonResponse
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from .models import Report, Profile, BugReport, Suggestion
from matches.models import MatchSupport, Match
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.contrib import messages
from functools import wraps
from django.utils import timezone



def is_admin(user):
    return user.is_superuser

def get_user_email(user):
    return get_object_or_404(EmailAddress, user=user, primary=True)

def check_email_verification(user):
    user_email = get_user_email(user)
    return user_email.verified if user_email else False

def request_verification(request):
    user_email = get_user_email(request.user)
    return render(request, 'request_verification.html', {'user_email': user_email})

def resend_verification(request):
    if request.user.is_authenticated and not request.user.emailaddress_set.filter(verified=True).exists():
        send_email_confirmation(request, request.user)
        messages.success(request, 'Verification email resent successfully!')
    else:
        messages.error(request, 'Your email is already verified or you are not logged in.')

    return redirect('home')  # Redirect to an appropriate view after attempting to resend the email

def email_verified_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            email = EmailAddress.objects.filter(user=request.user, verified=True).exists()
            if not email:
                return redirect('request_verification')  # Redirect to the email verification page
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page after successful login
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to home page after logout


def redirect_after_steam_login(request):
    if request.user.is_authenticated:
        if request.user.steam_id:
            # User has a Steam ID, redirect them to the home page
            return redirect('home')
        else:
            # User does not have a Steam ID, redirect them to customize_profile
            return redirect('customize_profile')
    else:
        # User is not authenticated, redirect them to the login page
        return redirect('home')

@login_required
def customize_profile_view(request):
    # Fetch the Profile model associated with the current user
    try:
        profile = request.user
    except Profile.DoesNotExist:
        profile = None



    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save the form data to the Profile model
            profile = form.save(commit=False)  # Save without committing to the database yet

            # Save the changes to the Profile model
            profile.save()


            return redirect('home')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'customize_profile.html', {'form': form})

@login_required
def profile_view(request):
    try:
        profile = request.user
    except Profile.DoesNotExist:
        profile = None

    steam_avatar = None
    steam_username = None

    try:
        steam_account = SocialAccount.objects.get(user=request.user, provider='steam')
        steam_avatar = steam_account.extra_data.get('avatarfull')
        steam_username = steam_account.extra_data.get('personaname')
    except SocialAccount.DoesNotExist:
        pass

    user_team = profile.current_team  # Access the current team of the user's profile

    # Fetch matches where the current user's team was involved (either as team1 or team2)
    past_matches = Match.objects.filter(
        match_completed=True,
        team1=user_team
    ) | Match.objects.filter(
        match_completed=True,
        team2=user_team
    ).order_by('-date')

    # Fetch current/upcoming matches
    upcoming_matches = Match.objects.filter(
        match_completed=False,
    ).order_by('date')

    return render(request, 'profile.html', {
        'profile': profile,
        'steam_avatar': steam_avatar,
        'steam_username': steam_username,
        'past_matches': past_matches,
        'upcoming_matches': upcoming_matches,  # Rename the variable to differentiate between past and upcoming matches
    })


    


User = get_user_model()
def other_profile_view(request, username):
    other_user = get_object_or_404(User, username=username)


    if other_user == request.user:
        return redirect('profile')

    steam_avatar = None
    steam_username = None
    try:
        steam_account = SocialAccount.objects.get(user=other_user, provider='steam')
        steam_avatar = steam_account.extra_data.get('avatarfull')
        steam_username = steam_account.extra_data.get('personaname')
    except SocialAccount.DoesNotExist:
        pass

    reported_user = other_user


    user_team = other_user.current_team  # Access the current team of the user's profile

    # Fetch matches where the current user's team was involved (either as team1 or team2)
    past_matches = Match.objects.filter(
        match_completed=True,
        team1=user_team
    ) | Match.objects.filter(
        match_completed=True,
        team2=user_team
    ).order_by('-date')

    # Fetch current/upcoming matches
    upcoming_matches = Match.objects.filter(
        match_completed=False,
    ).order_by('date')

    return render(request, 'other_profile.html', {
        'other_user': other_user,
        'steam_avatar': steam_avatar,
        'steam_username': steam_username,
        'reported_user': reported_user,
        'past_matches': past_matches,
        'upcoming_matches': upcoming_matches,
    })

    if other_user == request.user:
        return redirect('profile')

def banned_page(request):
    return render(request, 'banned_page.html')

@login_required
def report_user(request, username):
    reported_user = get_object_or_404(User, username=username)

    if reported_user == request.user:
        return redirect('profile')

    
    is_verified = check_email_verification(request.user)

    if is_verified:
        if request.method == 'POST':
            form = ReportForm(request.POST)
            if form.is_valid():
                reason = form.cleaned_data['reason']
                
                existing_report = Report.objects.filter(reporter=request.user, reported_user=reported_user).exists()
                if existing_report:
                    return JsonResponse({'success': False, 'message': 'You may have already reported this user.'})

                # Create a new report instance 
                Report.objects.create(reporter=request.user, reported_user=reported_user, reason=reason)

                # Redirect with a success message or display a success message on the same page
                return JsonResponse({'success': True})

                
        else:
            form = ReportForm()

        return render(request, 'report_user.html', {'form': form, 'reported_user': reported_user})
    else:
        return redirect('request_verification')

@user_passes_test(is_admin)
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        if 'ban_user' in request.POST:
            # Ban the reported user by setting is_banned to True
            reported_user = report.reported_user
            reported_user.is_banned = True
            reported_user.save()
            return redirect('report_detail', report_id=report_id)
    
    return render(request, 'report_detail.html', {'report': report})


@user_passes_test(is_admin)
def report_list(request):
    reports = Report.objects.all()
    return render(request, 'report_list.html', {'reports': reports})

@user_passes_test(is_admin)
def admin_center(request):
    return render(request, 'admin_center.html')

@user_passes_test(is_admin)
def banned_users_list(request):
    banned_users = User.objects.filter(is_banned=True)
    return render(request, 'banned_users_list.html', {'banned_users': banned_users})

@user_passes_test(is_admin)
def unban_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            user.is_banned = False
            user.save()
        except User.DoesNotExist:
            pass
    return redirect('banned_users_list')

@user_passes_test(is_admin)
def bug_report_list(request):
    open_bug_reports = BugReport.objects.filter(status='open')
    closed_bug_reports = BugReport.objects.filter(status='closed')

    context = {
        'open_bug_reports': open_bug_reports,
        'closed_bug_reports': closed_bug_reports,
    }

    return render(request, 'bug_report_list.html', context)

@user_passes_test(is_admin)
def suggestion_list(request):
    open_suggestion = Suggestion.objects.filter(status='open')
    closed_suggestion = Suggestion.objects.filter(status='closed')

    context = {
        'open_suggestion': open_suggestion,
        'closed_suggestion': closed_suggestion,
    }

    return render(request, 'suggestion_list.html', context)


@user_passes_test(is_admin)
def support_list(request):
    open_support = MatchSupport.objects.filter(status='open')
    closed_support = MatchSupport.objects.filter(status='closed')

    context = {
        'open_support': open_support,
        'closed_support': closed_support,
    }

    return render(request, 'support_list.html', context)


@user_passes_test(is_admin)
def support_detail(request, support_id):
    support = get_object_or_404(MatchSupport, id=support_id)
    return render(request, 'support_detail.html', {'support': support})

@user_passes_test(is_admin)
def bug_report_detail(request, bug_report_id):
    bug_report = get_object_or_404(BugReport, id=bug_report_id)
    return render(request, 'bug_report_detail.html', {'bug_report': bug_report})

@user_passes_test(is_admin)
def suggestion_detail(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion, id=suggestion_id)
    return render(request, 'suggestion_detail.html', {'suggestion': suggestion})

@user_passes_test(is_admin)
def change_bug_status(request, bug_report_id):
    bug_report = BugReport.objects.get(id=bug_report_id)
    # Update the status to 'Closed'
    bug_report.status = 'closed'
    bug_report.save()
    return redirect('bug_report_detail', bug_report_id=bug_report_id)

def player_ladder_view(request):
    # Get all users
    all_users = Profile.objects.all().order_by('-rating')

    context = {'all_users': all_users}
    return render(request, 'player_ladder.html', context)

def report_bug(request):
    is_verified = check_email_verification(request.user)

    if is_verified:
        if request.method == 'POST':
            form = BugReportForm(request.POST)
            if form.is_valid():
                bug_report = form.save(commit=False)
                if request.user.is_authenticated:
                    bug_report.reporter = request.user
                bug_report.save()
                return redirect('home')  # Redirect to a confirmation page
        else:
            form = BugReportForm()
        return render(request, 'report_bug.html', {'form': form})
    else:
        return redirect('request_verification')


def reset_eligibility(user):
    if user:
        user.eligible = False
        user.eligible_at = timezone.now() + timezone.timedelta(hours=3)
        user.save()

def check_eligibility(user):
    if user.is_authenticated:
        if user.eligible_at < timezone.now():
           user.eligible = True
           user.save()


def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms(request):
    return render(request, 'terms.html')


def create_suggestion(request):
    is_verified = check_email_verification(request.user)

    if is_verified:
        if request.method == 'POST':
            form = SuggestionForm(request.POST)
            if form.is_valid():
                suggestion = form.save(commit=False)
                if request.user.is_authenticated:
                    suggestion.reporter = request.user
                suggestion.save()
                return redirect('home')  # Redirect to a confirmation page
        else:
            form = BugReportForm()
        return render(request, 'create_suggestion.html', {'form': form})
    else:
        return redirect('request_verification')

@user_passes_test(is_admin)
def change_suggestion_status(request, suggestion_id):
    suggestion = Suggestion.objects.get(pk=suggestion_id)
    # Update the status to 'Closed'
    suggestion.status = 'closed'
    suggestion.save()
    return redirect('suggestion_detail', suggestion_id=suggestion_id)

@user_passes_test(is_admin)
def change_support_status(request, support_id):
    support = MatchSupport.objects.get(pk=support_id)
    # Update the status to 'Closed'
    support.status = 'closed'
    support.save()
    return redirect('support_detail', support_id=support_id)