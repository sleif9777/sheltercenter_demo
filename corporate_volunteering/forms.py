import numpy as np

from django import forms

from .models import *

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            'org_name',
            'leader_fname',
            'leader_lname',
            'contact_email',
            'auth_code',
        ]
        labels = {
            'org_name': 'Organization Name:',
            'leader_fname': 'Team Leader First Name:',
            'leader_lname': 'Team Leader Last Name:',
            'contact_email': "Contact Email:",
            'auth_code': 'Authorization Code:',
        }
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.fields['auth_code'].disabled = True


class EventForm(forms.ModelForm):
    class Meta:
        model = VolunteeringEvent
        fields = [
            'date',
            'organization',
            'event_counselor',
            'activity_level',
            'event_task',
            'headcount',
            'notes'
        ]
        labels = {
            'date': "Date: ",
            'organization': "Organization: ",
            'event_counselor': "Counselor: ",
            'event_task': "This group will be helping with ",
            'headcount': "Volunteer headcount: ",
        }
        widgets = {
            'date': forms.SelectDateWidget(),
            'event_task': forms.TextInput(attrs={'size': 120}),
        }
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(EventForm, self).__init__(*args, **kwargs)


# class EventConfirmHeadcountForm(forms.ModelForm):
#     class Meta:
#         model = VolunteeringEvent
#         fields = [
#             'volunteer_confirmed_count',
#         ]
#         labels = {
#             'volunteer_confirmed_count': "Confirmed Volunteer Count: ",
#         }
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault('label_suffix', '')
#         super(EventForm, self).__init__(*args, **kwargs)


class EventTimeForm(forms.Form):
    HOUR_CHOICES = [
        (str(i), str(i)) for i in range(1, 13)
    ]

    MINUTE_CHOICES = [
        (str(i), str(i).zfill(2)) for i in range(0, 60, 15)
    ]

    DAYPART_CHOICES = [
        ("0", "AM"),
        ("1", "PM"),
    ]

    start_hour = forms.ChoiceField(choices = HOUR_CHOICES, label="Select a start time")
    start_minute = forms.ChoiceField(choices = MINUTE_CHOICES, label=":")
    start_daypart = forms.ChoiceField(choices = DAYPART_CHOICES, label="")

    end_hour = forms.ChoiceField(choices = HOUR_CHOICES, label="Select an end time")
    end_minute = forms.ChoiceField(choices = MINUTE_CHOICES, label=":")
    end_daypart = forms.ChoiceField(choices = DAYPART_CHOICES, label="")

    class Meta:
        labels = {
            'start_hour': 'Select a start time',
            'start_minute': '',
            'start_daypart': '',
            'end_hour': 'Select a start time',
            'end_minute': '',
            'end_daypart': ''
        }
