from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.urls import re_path

urlpatterns = [
    path('', views.home_view, name='home'),
    path('ladders/', views.ladders, name='ladders'),
    path('my_teams/', views.my_teams, name='my_teams')


]

