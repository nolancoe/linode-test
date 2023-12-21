# forms.py
from django import forms
from .models import Challenge, Match, MatchResult, DisputeProof, DirectChallenge, MatchSupport, SupportCategory
from django.utils import timezone
from users.models import Profile
from django.core.exceptions import ValidationError


class ChallengeForm(forms.ModelForm):
    search_only = forms.BooleanField(label='Search Only', required=False)
    controller_only = forms.BooleanField(label='Controller Only', required=False)
    challenge_players = forms.ModelMultipleChoiceField(queryset=None, required=True, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Challenge
        fields = ['scheduled_date', 'search_only', 'controller_only', 'challenge_players']

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            players_queryset = team.players.filter(eligible=True)
            self.fields['challenge_players'].queryset = players_queryset

    def clean(self):
        cleaned_data = super().clean()
        selected_players = cleaned_data.get('challenge_players')
        
        # Check if exactly 4 players are selected
        if selected_players.count() != 4:
            raise ValidationError("Please select exactly 4 players.")

        return cleaned_data

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date:
            # Convert scheduled date to UTC
            user_timezone = self.user.timezone  # Make sure 'user' is available in the form
            utc_offset = user_timezone.utcoffset(scheduled_date).total_seconds()
            utc_scheduled_date = scheduled_date - timezone.timedelta(seconds=utc_offset)
            return utc_scheduled_date

class DirectChallengeForm(forms.ModelForm):
    search_only = forms.BooleanField(label='Search Only', required=False)
    controller_only = forms.BooleanField(label='Controller Only', required=False)
    challenge_players = forms.ModelMultipleChoiceField(queryset=None, required=True, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = DirectChallenge
        fields = ['scheduled_date', 'search_only', 'controller_only', 'challenge_players']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            current_team = user.current_team
            if current_team:
                players_queryset = current_team.players.all()
                self.fields['challenge_players'].queryset = players_queryset
                

    def clean(self):
        cleaned_data = super().clean()
        selected_players = cleaned_data.get('challenge_players')
        
        # Check if exactly 4 players are selected
        if selected_players.count() != 4:
            raise ValidationError("Please select exactly 4 players.")

        return cleaned_data

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
            'claim': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'additional_evidence': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
class MatchSupportForm(forms.ModelForm):
    class Meta:
        model = MatchSupport
        fields = ['category', 'description', 'additional_evidence']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = SupportCategory.objects.all()



class PlayerSelectionForm(forms.Form):
    challenge_players = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        team_players = kwargs.pop('team_players', None)
        super().__init__(*args, **kwargs)
        if team_players:
            self.fields['challenge_players'].queryset = team_players.filter(eligible=True)

    def clean_challenge_players(self):
        selected_players = self.cleaned_data.get('challenge_players')
        if len(selected_players) != 4:
            raise ValidationError("Please select exactly 4 players.")
        return selected_players