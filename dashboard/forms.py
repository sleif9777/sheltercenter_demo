from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from tinymce.widgets import TinyMCE

from .models import *

class CreateAdminForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class EmailSigForm(forms.ModelForm):

    signature = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Profile
        fields = [
            'signature',
        ]
        labels = {
            'signature': 'Set your email signature here:'
        }
