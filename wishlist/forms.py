from django import forms
from tinymce.widgets import TinyMCE

from .models import *

class DogOffsiteForm(forms.ModelForm):
    class Meta:
        model = Dog
        fields = [
            'offsite',
        ]
        widgets = {

        }
        labels = {
            'offsite': 'Appointment Only? ',
        }
