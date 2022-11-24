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

class AppointmentCardPreferences(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'ac_show_number_of_visits',
            'ac_show_adopter_email',
            'ac_show_adopter_phone',
            'ac_show_adopter_description',
            'ac_show_counselor',
            'ac_show_internal_notes',
            'ac_show_adopter_notes',
            'ac_show_shelterluv_notes',
            'ac_show_city_state',
            'ac_show_household_activity',
            'ac_show_housing',
            'ac_show_fence',
            'ac_show_booking_timestamp',
            'ac_show_gender_preference',
            'ac_show_weight_preference',
            'ac_show_age_preference',
            'ac_show_hypo_preference',
            'ac_show_breed_restriction_comm',
            'ac_show_dogs_adopted_comm',
            'ac_show_limited_small_dogs_comm',
            'ac_show_limited_small_puppies_comm',
            'ac_show_lives_with_parents_comm',
            'ac_show_limited_puppies_comm',
            'ac_show_limited_hypo_comm',
            'ac_show_send_follow_up',
            'ac_show_send_follow_up_with_host',
            'ac_show_schedule_next',
        ]
