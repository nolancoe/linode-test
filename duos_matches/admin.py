from django.contrib import admin
from .models import DuosMatch, DuosChallenge, DuosMatchResult, DuosDispute, DuosDisputeProof, DuosDirectChallenge, DuosMatchSupport

# Register your custom Profile model
admin.site.register(DuosMatch)
admin.site.register(DuosChallenge)
admin.site.register(DuosMatchResult)
admin.site.register(DuosDispute)
admin.site.register(DuosDisputeProof)
admin.site.register(DuosDirectChallenge)
admin.site.register(DuosMatchSupport)
