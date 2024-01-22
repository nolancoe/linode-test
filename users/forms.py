from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Profile, BugReport, Suggestion
from django.contrib.auth.forms import AuthenticationForm
import pytz

class ProfileForm(forms.ModelForm):

    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.all_timezones], label='Timezone')

    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'birthday', 'country', 'timezone', 'profile_picture', 'gamertag', 'psnid', 'twitter_link', 'youtube_link', 'activision_id']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Birthday'}),
            'country': CountrySelectWidget(attrs={'class': 'form-control custom-select', 'placeholder': 'Country'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email Address'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'twitter_link': forms.TextInput(attrs={'placeholder': 'Twitter Link'}),
            'youtube_link': forms.TextInput(attrs={'placeholder': 'Youtube Link'}),
            'activision_id': forms.TextInput(attrs={'placeholder': 'Activision ID'}),
            'gamertag': forms.TextInput(attrs={'placeholder': 'Xbox Gamertag'}),
            'psnid': forms.TextInput(attrs={'placeholder': 'Playstation Network ID'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),

        }



class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class ReportForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))


class BugReportForm(forms.ModelForm):
    class Meta:
        model = BugReport
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['description']
        widgets = {
            'suggestion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }