from django.contrib import admin
from .models import DuosTeam, DuosTeamInvitation

# Register your custom Profile model
admin.site.register(DuosTeam)
admin.site.register(DuosTeamInvitation)