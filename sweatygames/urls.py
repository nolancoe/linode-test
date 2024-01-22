"""
URL configuration for sweatygames project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # Import the include function
from django.conf.urls.static import static
from django.conf import settings
from users.views import support_list, change_support_status, support_detail, create_suggestion, suggestion_list, change_suggestion_status, suggestion_detail, terms, email_verified_required, privacy_policy, request_verification, resend_verification, login_view, logout_view, player_ladder_view, banned_page, report_user, report_detail, admin_center, unban_user, banned_users_list, report_list, customize_profile_view, profile_view, redirect_after_steam_login, other_profile_view, report_bug, bug_report_list, bug_report_detail, change_bug_status
from teams.views import create_team, already_a_player, team_ladder, invitation_sent, invitation_already_sent, transfer_ownership, edit_team, user_is_teammate, send_invitation, pending_team_invites, accept_invitation, team_detail, remove_player_from_team, leave_team, deny_invitation, disband_team
from matches.views import dispute_under_review, support_request_success, rules, request_match_support, submit_results_success, dispute_conflict, team_not_eligible, decline_direct_challenge, match_farming, schedule_conflict, accept_challenge, accept_direct_challenge, create_challenge, challenges, match_details, submit_results, dispute_proofs_list, update_dispute_proof, dispute_proof_details, dispute_details, disputes_list, match_list, past_match_list, my_match_list, my_past_match_list, cancel_challenge, cancel_direct_challenge, my_challenges_view, dispute_expired, create_direct_challenge
from messaging.views import messages, message_details, send_message
from duos_teams.views import create_duos_team, duos_team_ladder, edit_duos_team, send_duos_invitation, duos_invitation_sent, pending_duos_team_invites, duos_invitation_already_sent, user_is_duos_teammate, deny_duos_invitation, accept_duos_invitation, duos_team_detail, remove_player_from_duos_team, transfer_duos_ownership, leave_duos_team, disband_duos_team
from duos_matches.views import create_duos_challenge, duos_dispute_proof_details, cancel_direct_duos_challenge, accept_direct_duos_challenge, decline_direct_duos_challenge, my_duos_challenges,  duos_support_list, duos_support_detail, change_duos_support_status, create_direct_duos_challenge, accept_duos_challenge, duos_challenges, cancel_duos_challenge, duos_match_details, update_duos_dispute_proof, submit_duos_results, duos_dispute_proofs_list, duos_dispute_details, duos_disputes_list, duos_match_list, past_duos_match_list, my_duos_match_list, request_duos_match_support, my_past_duos_match_list

urlpatterns = [
    path('yougottatryharderthanthathackercmonnow/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/<str:username>/', other_profile_view, name='other_user_profile'),
    path('admin_center/', admin_center, name='admin_center'),
    path('banned-users/', banned_users_list, name='banned_users_list'),
    path('unban-user/', unban_user, name='unban_user'),

    path('accounts/', include('allauth.urls')),

    path('request_verification/', request_verification, name='request_verification'),
    path('resend-verification/', resend_verification, name='resend_verification'),


    

    path('customize_profile/', customize_profile_view, name='customize_profile'),
    path('redirect_after_steam_login/', redirect_after_steam_login, name='redirect_after_steam_login'),
    path('banned/', banned_page, name='banned_page'),
    path('report_user/<str:username>/', report_user, name='report_user'),
    path('report/<int:report_id>/', report_detail, name='report_detail'),
    path('reports/', report_list, name='report_list'),
    path('report_bug/', report_bug, name='report_bug'),
    path('bug_report_list/', bug_report_list, name='bug_report_list'),
    path('bug_report_detail/<int:bug_report_id>/', bug_report_detail, name='bug_report_detail'),
    path('bug_report_detail/<int:bug_report_id>/change_status/', change_bug_status, name='change_bug_status'),
    path('create_suggestion/', create_suggestion, name='create_suggestion'),
    path('suggestion_detail/<int:suggestion_id>/', suggestion_detail, name='suggestion_detail'),
    path('suggestion_detail/<int:suggestion_id>/change_status/', change_suggestion_status, name='change_suggestion_status'),
    path('suggestion_list/', suggestion_list, name='suggestion_list'),

    #Team Links
    path('create_team/', create_team, name='create_team'),
    path('already_a_player/', already_a_player, name='already_a_player'),
    path('invitation_sent/', invitation_sent, name='invitation_sent'),
    path('invitation_already_sent/', invitation_already_sent, name='invitation_already_sent'),
    path('user_is_teammate/', user_is_teammate, name='user_is_teammate'),
    path('invite/<int:team_id>/', send_invitation, name='send_invitation'),

    path('pending_team_invites/', pending_team_invites, name='pending_team_invites'),
    path('accept_invitation/<int:invitation_id>/', accept_invitation, name='accept_invitation'),
    path('team/<int:team_id>/remove_player/<int:player_id>/', remove_player_from_team, name='remove_player_from_team'),
    path('team/<int:team_id>/leave/', leave_team, name='leave_team'),
    path('team/<int:team_id>/', team_detail, name='team_detail'),
    path('deny_invitation/<int:invitation_id>/', deny_invitation, name='deny_invitation'),
    path('disband_team/<int:team_id>/', disband_team, name='disband_team'),
    path('team/edit/<int:team_id>/', edit_team, name='edit_team'),
    path('team_ladder/', team_ladder, name='team_ladder'),
    path('player_ladder/', player_ladder_view, name='player_ladder'),
    path('transfer_ownership/<int:team_id>/<int:new_owner_id>/', transfer_ownership, name='transfer_ownership'),

    #Duos Team Links
    path('create_duos_team/', create_duos_team, name='create_duos_team'),
    path('duos_team_ladder/', duos_team_ladder, name='duos_team_ladder'),
    path('duos_team/edit/<int:team_id>/', edit_duos_team, name='edit_duos_team'),
    path('duos_invite/<int:team_id>/', send_duos_invitation, name='send_duos_invitation'),
    path('duos_invitation_sent/', duos_invitation_sent, name='duos_invitation_sent'),
    path('duos_invitation_already_sent/', duos_invitation_already_sent, name='duos_invitation_already_sent'),
    path('user_is_duos_teammate/', user_is_duos_teammate, name='user_is_duos_teammate'),
    path('accept_duos_invitation/<int:invitation_id>/', accept_duos_invitation, name='accept_duos_invitation'),
    path('deny_duos_invitation/<int:invitation_id>/', deny_duos_invitation, name='deny_duos_invitation'),
    path('pending_duos_team_invites/', pending_duos_team_invites, name='pending_duos_team_invites'),
    path('duos_team/<int:team_id>/', duos_team_detail, name='duos_team_detail'),
    path('duos_team/<int:team_id>/remove_player/<int:player_id>/', remove_player_from_duos_team, name='remove_player_from_duos_team'),
    path('transfer_duos_ownership/<int:team_id>/<int:new_owner_id>/', transfer_duos_ownership, name='transfer_duos_ownership'),
    path('duos_team/<int:team_id>/leave/', leave_duos_team, name='leave_duos_team'),
    path('disband_duos_team/<int:team_id>/', disband_duos_team, name='disband_duos_team'),


    #Match Links
    path('challenges/', email_verified_required(challenges), name='challenges'),
    path('create_challenge/', email_verified_required(create_challenge), name='create_challenge'),
    path('accept_challenge/<int:challenge_id>/', accept_challenge, name='accept_challenge'),
    path('accept_direct_challenge/<int:direct_challenge_id>/', accept_direct_challenge, name='accept_direct_challenge'),
    path('create_direct_challenge/<int:team_id>/', email_verified_required(create_direct_challenge), name='create_direct_challenge'),
    path('cancel_challenge/<int:challenge_id>/', cancel_challenge, name='cancel_challenge'),
    path('cancel_direct_challenge/<int:direct_challenge_id>/', cancel_direct_challenge, name='cancel_direct_challenge'),
    path('match/<int:match_id>/', match_details, name='match_details'),
    path('match/<int:match_id>/submit_results/', submit_results, name='submit_results'),
    path('update_dispute_proof/<int:proof_id>/', update_dispute_proof, name='update_dispute_proof'),
    path('dispute_proofs/', dispute_proofs_list, name='dispute_proofs_list'),
    path('dispute_proof/<int:proof_id>/', dispute_proof_details, name='dispute_proof_details'),
    path('dispute/<int:dispute_id>/', dispute_details, name='dispute_details'),
    path('disputes/', disputes_list, name='disputes_list'),
    path('matches/', match_list, name='match_list'),
    path('past_matches/', past_match_list, name='past_match_list'),
    path('my_matches/', my_match_list, name='my_match_list'),
    path('my_past_matches/', my_past_match_list, name='my_past_match_list'),
    path('my_challenges/', my_challenges_view, name='my_challenges'),
    path('decline_direct_challenge/<int:challenge_id>/', decline_direct_challenge, name='decline_direct_challenge'),

    path('schedule_conflict/', schedule_conflict, name='schedule_conflict'),
    path('match_farming/', match_farming, name='match_farming'),
    path('submit_results_success/', submit_results_success, name='submit_results_success'),
    path('dispute_expired/', dispute_expired, name='dispute_expired'),
    path('dispute_under_review/', dispute_under_review, name='dispute_under_review'),
    path('dispute_conflict/', dispute_conflict, name='dispute_conflict'),
    path('team_not_eligible/', team_not_eligible, name='team_not_eligible'),
    


    #Duos Match Links
    path('duos_challenges/', email_verified_required(duos_challenges), name='duos_challenges'),
    path('create_duos_challenge/', email_verified_required(create_duos_challenge), name='create_duos_challenge'),
    path('create_direct_duos_challenge/<int:team_id>/', email_verified_required(create_direct_duos_challenge), name='create_direct_duos_challenge'),
    path('accept_duos_challenge/<int:challenge_id>/', accept_duos_challenge, name='accept_duos_challenge'),
    path('cancel_duos_challenge/<int:challenge_id>/', cancel_duos_challenge, name='cancel_duos_challenge'),
    path('cancel_direct_duos_challenge/<int:direct_challenge_id>/', cancel_direct_duos_challenge, name='cancel_direct_duos_challenge'),
    path('decline_direct_duos_challenge/<int:challenge_id>/', decline_direct_duos_challenge, name='decline_direct_duos_challenge'),
    path('accept_direct_duos_challenge/<int:direct_challenge_id>/', accept_direct_duos_challenge, name='accept_direct_duos_challenge'),
    path('duos_match/<int:match_id>/', duos_match_details, name='duos_match_details'),
    path('update_duos_dispute_proof/<int:proof_id>/', update_duos_dispute_proof, name='update_duos_dispute_proof'),
    path('duos_match/<int:match_id>/submit_results/', submit_duos_results, name='submit_duos_results'),
    path('duos_dispute_proofs/', duos_dispute_proofs_list, name='duos_dispute_proofs_list'),
    path('duos_dispute/<int:dispute_id>/', duos_dispute_details, name='duos_dispute_details'),
    path('duos_disputes/', duos_disputes_list, name='duos_disputes_list'),
    path('duos_matches/', duos_match_list, name='duos_match_list'),
    path('past_duos_matches/', past_duos_match_list, name='past_duos_match_list'),
    path('my_duos_matches/', my_duos_match_list, name='my_duos_match_list'),
    path('my_past_duos_matches/', my_past_duos_match_list, name='my_past_duos_match_list'),
    path('request_duos_match_support/<int:match_id>/', request_duos_match_support, name='request_duos_match_support'),
    path('duos_support_detail/<int:support_id>/change_status/', change_duos_support_status, name='change_support_status'),
    path('duos_support_detail/<int:support_id>/', duos_support_detail, name='duos_support_detail'),
    path('my_duos_challenges/', my_duos_challenges, name='my_duos_challenges'),
    path('duos_dispute_proof/<int:proof_id>/', duos_dispute_proof_details, name='duos_dispute_proof_details'),



    path('privacy_policy/', privacy_policy, name='privacy_policy'),
    path('terms/', terms, name='terms'),
    path('rules/', rules, name='rules'),

    path('request_match_support/<int:match_id>/', request_match_support, name='request_match_support'),
    path('support_request_success/', support_request_success, name='support_request_success'),
    path('support_detail/<int:support_id>/', support_detail, name='support_detail'),
    path('support_detail/<int:support_id>/change_status/', change_support_status, name='change_support_status'),
    path('support_list/', support_list, name='support_list'),
    path('duos_support_list/', duos_support_list, name='duos_support_list'),



    path('messages/', email_verified_required(messages), name='messages'),
    path('messages/<str:username>/', email_verified_required(message_details), name='message_details'),
    path('messages/<str:username>/send/', email_verified_required(send_message), name='send_message'),


    path('', include('core.urls')),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

