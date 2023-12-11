# users/admin.py
from django.contrib import admin
from .models import Profile, Report, BugReport, Suggestion, Badge

# Register your custom Profile model
admin.site.register(Profile)
admin.site.register(Report)
admin.site.register(BugReport)
admin.site.register(Suggestion)
admin.site.register(Badge)