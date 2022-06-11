from django import forms
import datetime
from .models import Adopter
from tinymce.widgets import TinyMCE

class AdopterForm(forms.ModelForm):
    class Meta:
        model = Adopter
        fields = [
            'f_name',
            'l_name',
            'primary_email',
            'status',
            'carryover_shelterluv',
            'out_of_state',
            'lives_with_parents',
            'adopting_host',
            'adopting_foster',
            'chosen_dog',
            'app_interest'
        ]
        labels = {
            'f_name': 'First Name:',
            'l_name': 'Last Name:',
            'primary_email': 'Email:',
            'status': 'Status:',
            'carryover_shelterluv': 'Adopter was in Shelterluv before ShelterCenter went live',
            'out_of_state': 'Adopter from outside NC, SC, or VA',
            'lives_with_parents': 'Adopter lives with parents',
            'adopting_host': 'Adopting their host dog',
            'adopting_foster': 'Adopting their foster dog',
            'chosen_dog': '(For foster/host adoptions) Chosen dog:',
            'app_interest': '(For general adoptions) Interested in:'
        }
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(AdopterForm, self).__init__(*args, **kwargs)

class AdopterPreferenceForm(forms.ModelForm):
    class Meta:
        model = Adopter
        fields = [
            'gender_preference',
            'age_preference',
            'min_weight',
            'max_weight',
            'hypo_preferred',
        ]
        labels = {
            'min_weight': "Minimum desired weight (optional)",
            'max_weight': "Maximum desired weight (optional)",
            'hypo_preferred': "I am only looking for a low-shed or hypoallergenic dog"
        }

class SetAlertDateForm(forms.ModelForm):
    class Meta:
        model = Adopter
        fields = [
            'alert_date'
        ]
        labels = {
            'alert_date': "",
        }
        widgets = {
            'alert_date': forms.SelectDateWidget()
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(SetAlertDateForm, self).__init__(*args, **kwargs)

class ContactUsForm(forms.Form):
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

class AdopterCSVForm(forms.Form):
    file = forms.FileField(label = "Upload a CSV file to add adopters", required = True)

class ContactAdopterForm(forms.Form):
    message = forms.CharField(label = "", widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

class AdopterLoginField(forms.Form):
    email = forms.EmailField(label='Please enter the email attached to your application', widget=forms.EmailInput(attrs={'class':'special', 'size': '40'}))
