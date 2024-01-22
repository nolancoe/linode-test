from django import forms
from .models import Team
from users.models import Profile
from .models import TeamInvitation


class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'logo']
        widgets = {
            
            'name': forms.TextInput(attrs={'placeholder': 'Team Name'}),

        }
    
class TeamInvitationForm(forms.ModelForm):
    class Meta:
        model = TeamInvitation
        fields = ['invited_user']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request and request.user.is_authenticated:
            current_user_team = request.user.current_team
            self.fields['invited_user'].queryset = Profile.objects.filter(
                Q(current_team__isnull=True) | Q(current_team=current_user_team)
            ).exclude(id=request.user.id)

        self.fields['invited_user'].widget.attrs['class'] = 'form-control'