# users/admin.py
from django.contrib import admin
from .models import Profile, Report, BugReport, Suggestion, Badge


class CustomProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'eligible')  # Add 'twitch_link_column' and 'eligible'


# Register your custom Profile model
admin.site.register(Profile, CustomProfileAdmin)
admin.site.register(Report)
admin.site.register(BugReport)
admin.site.register(Suggestion)
admin.site.register(Badge)


