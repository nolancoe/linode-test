from django import forms
from .models import DuosTeam
from users.models import Profile
from .models import DuosTeamInvitation


class DuosTeamCreationForm(forms.ModelForm):
    class Meta:
        model = DuosTeam
        fields = ['name', 'logo']
        widgets = {
            
            'name': forms.TextInput(attrs={'placeholder': 'Team Name'}),

        }
    
class DuosTeamInvitationForm(forms.ModelForm):
    class Meta:
        model = DuosTeamInvitation
        fields = ['invited_user']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request and request.user.is_authenticated:
            current_user_team = request.user.current_duos_team
            self.fields['invited_user'].queryset = Profile.objects.filter(
                Q(current_team__isnull=True) | Q(current_team=current_user_team)
            ).exclude(id=request.user.id)

        self.fields['invited_user'].widget.attrs['class'] = 'form-control'