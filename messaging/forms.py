from django import forms

class MessageForm(forms.Form):
    message_content = forms.CharField(widget=forms.Textarea)