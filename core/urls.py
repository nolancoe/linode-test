from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.urls import re_path

urlpatterns = [
    path('', views.home_view, name='home'),
    path('ladders/', views.ladders, name='ladders'),
    path('my_teams/', views.my_teams, name='my_teams'),
    path('my_challenges_picker/', views.my_challenges_picker, name='my_challenges_picker'),
    path('my_matches_picker/', views.my_matches_picker, name='my_matches_picker'),
    path('disputes_picker/', views.disputes_picker, name='disputes_picker'),
    path('team_invites_picker/', views.team_invites_picker, name='team_invites_picker'),
    path('challenges_picker/', views.challenges_picker, name='challenges_picker'),
    path('matches_picker/', views.matches_picker, name='matches_picker'),
    path('results_picker/', views.results_picker, name='results_picker'),


]

