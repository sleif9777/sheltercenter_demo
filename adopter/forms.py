from django import forms
import datetime
from .models import Adopter
from tinymce.widgets import TinyMCE

class AdopterForm(forms.ModelForm):
    class Meta:
        model = Adopter
        fields = [
            'adopter_first_name',
            'adopter_last_name',
            'adopter_email',
            'status',
            'out_of_state',
            'lives_with_parents',
            'adopting_host',
            'adopting_foster',
            'friend_of_foster',
            'chosen_dog',
            'app_interest'
        ]
        labels = {
            'adopter_first_name': 'First Name:',
            'adopter_last_name': 'Last Name:',
            'adopter_email': 'Email:',
            'status': 'Status:',
            'out_of_state': 'Adopter from outside NC, SC, or VA',
            'lives_with_parents': 'Adopter lives with parents',
            'adopting_host': 'Adopting their host dog',
            'adopting_foster': 'Adopting their foster dog',
            'friend_of_foster': "Adopting a friend's foster dog",
            'chosen_dog': '(For foster/host adoptions) Chosen Dog:',
            'app_interest': '(For general adoptions) Interested in:'
        }
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(AdopterForm, self).__init__(*args, **kwargs)

# class SelectAdopterForm(forms.Form):
#     get_all_adopters = Adopter.objects
#     print("Adopters: " + str(get_all_adopters))
#     ALL_ADOPTERS = []
#
#     for adopter in get_all_adopters.iterator():
#         ALL_ADOPTERS += [(str(adopter.id), adopter.adopter_list_name())]
#
#     session_adopter = forms.ChoiceField(choices = ALL_ADOPTERS)

class ContactUsForm(forms.Form):
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

class AdopterCSVForm(forms.Form):
    file = forms.FileField(label = "Upload a CSV file to add adopters", required = True)

class ContactAdopterForm(forms.Form):
    message = forms.CharField(label = "", widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

class AdopterLoginField(forms.Form):
    email = forms.EmailField(label='Please enter the email attached to your application', widget=forms.EmailInput(attrs={'class':'special', 'size': '40'}))
