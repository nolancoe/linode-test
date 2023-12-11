# forms.py
from django import forms
from .models import Challenge, Match, MatchResult, DisputeProof, DirectChallenge, MatchSupport, SupportCategory
from django.utils import timezone

class ChallengeForm(forms.ModelForm):
    search_only = forms.BooleanField(label='Search Only', required=False)

    class Meta:
        model = Challenge
        fields = ['scheduled_date', 'search_only']

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        
        if scheduled_date:
            user_timezone = self.user.timezone
            utc_offset = user_timezone.utcoffset(scheduled_date).total_seconds()
            utc_scheduled_date = scheduled_date - timezone.timedelta(seconds=utc_offset)
            return utc_scheduled_date

class DirectChallengeForm(forms.ModelForm):
    search_only = forms.BooleanField(label='Search Only', required=False)

    class Meta:
        model = DirectChallenge
        fields = ['scheduled_date', 'search_only'] 

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        
        if scheduled_date:
            user_timezone = self.user.timezone
            utc_offset = user_timezone.utcoffset(scheduled_date).total_seconds()
            utc_scheduled_date = scheduled_date - timezone.timedelta(seconds=utc_offset)
            return utc_scheduled_date

class MatchResultForm(forms.ModelForm):
    team_result = forms.ChoiceField(
        choices=[('win', 'Win'), ('loss', 'Loss')],
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = MatchResult
        fields = ['team_result']

class DisputeProofForm(forms.ModelForm):
    class Meta:
        model = DisputeProof
        fields = ['game1_screenshot', 'game2_screenshot', 'game3_screenshot', 'claim', 'additional_evidence']
        widgets = {
            'claim': forms.Textarea(attrs={'rows': 4}),
            'additional_evidence': forms.Textarea(attrs={'rows': 4}),
        }
    
class MatchSupportForm(forms.ModelForm):
    class Meta:
        model = MatchSupport
        fields = ['category', 'description', 'additional_evidence']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = SupportCategory.objects.all()