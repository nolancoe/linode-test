from django.contrib import admin
from .models import Team, TeamInvitation

# Register your custom Profile model
admin.site.register(Team)
admin.site.register(TeamInvitation)