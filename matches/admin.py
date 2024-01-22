from django.contrib import admin
from .models import Match, Challenge, MatchResult, Dispute, DisputeProof, DirectChallenge, MatchSupport, SupportCategory

# Register your custom Profile model
admin.site.register(Match)
admin.site.register(Challenge)
admin.site.register(MatchResult)
admin.site.register(Dispute)
admin.site.register(DisputeProof)
admin.site.register(DirectChallenge)
admin.site.register(MatchSupport)
admin.site.register(SupportCategory)