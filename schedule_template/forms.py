import datetime
import os

from django import forms

from .models import AppointmentTemplate, TimeslotTemplate

class GenericAppointmentModelFormPrefilled(forms.ModelForm):
    class Meta:
        model = AppointmentTemplate
        fields = [
            'day_of_week',
            'time',
            'appt_type',
        ]
        widgets = {
            'day_of_week': forms.HiddenInput(),
            'time': forms.HiddenInput(),
        }
        labels = {
            'appt_type': 'Appointment Type',
        }

class GenericTimeslotModelFormPrefilled(forms.ModelForm):
    # appointments = forms.ModelMultipleChoiceField(queryset = AppointmentTemplate.objects.all(), required=False)

    class Meta:
        model = TimeslotTemplate
        fields = [
            'day_of_week',
            'time',
            'appointments',
        ]

        widgets = {
            'day_of_week': forms.HiddenInput(),
            'appointments': forms.MultipleHiddenInput(),
        }
    #
    # def __init__(self, *args, **kwargs):
    #     super(GenericTimeslotModelFormPrefilled, self).__init__(*args, **kwargs)
    #     self.fields['day_of_week'].initial = dow.day_of_week
    #     self.fields['appointments'].required = False

class NewTimeslotModelForm(forms.Form):
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

    hour = forms.ChoiceField(choices = HOUR_CHOICES, label="Select a time")
    minute = forms.ChoiceField(choices = MINUTE_CHOICES, label=":")
    daypart = forms.ChoiceField(choices = DAYPART_CHOICES, label="")

    class Meta:
        labels = {
            'hour': 'Select a time',
            'minute': '',
            'daypart': ''
        }
