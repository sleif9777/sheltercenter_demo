from django import forms
import datetime
from .models import *
from adopter.models import Adopter
import demo.settings as settings

class AppointmentModelFormPrefilled(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'date',
            'time',
            'appt_type',
            'adopter',
            'locked',
            'dog',
            'dog_fka',
            'internal_notes',
            'bringing_dog',
            'has_cat',
            'mobility'
        ]
        labels = {
            'date': 'Date:',
            'time': 'Time:',
            'appt_type': 'Appointment Type:',
            'adopter': 'Select Adopter:',
            'locked': 'Lock appointment?',
            'dog': '(For surrenders and paperwork appointments) Dog:',
            'dog_fka': '(For surrenders, if applicable) FKA:',
            'internal_notes': 'Notes:',
        }
        widgets = {
            'date': forms.HiddenInput(),
            'time': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(AppointmentModelFormPrefilled, self).__init__(*args, **kwargs)

class BookAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'adopter',
            'adopter_notes',
            'bringing_dog',
            'has_cat',
            'mobility'
        ]
        widgets = {
            'adopter': forms.HiddenInput(),
        }
        labels = {
            'adopter_notes': "",
            'bringing_dog': "Check this box if you plan to bring your current dog with you: ",
            'has_cat': "Check this box if you have a cat in the home: ",
            'mobility': "We are happy to accommodate visitors with limited mobility and are ADA compliant. If you have limited mobility, please check this box so we can be best prepared: "
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(BookAppointmentForm, self).__init__(*args, **kwargs)

class JumpToDateForm(forms.Form):
    date = forms.DateField(widget = forms.SelectDateWidget())

class DailyAnnouncementForm(forms.ModelForm):
    class Meta:
        model = DailyAnnouncement
        fields = [
            'date',
            'text'
        ]
        widgets = {
            'date': forms.HiddenInput(),
        }

class InternalAnnouncementForm(forms.ModelForm):
    class Meta:
        model = InternalAnnouncement
        fields = [
            'date',
            'text'
        ]
        widgets = {
            'date': forms.HiddenInput(),
        }

class CalendarAnnouncementForm(forms.ModelForm):
    class Meta:
        model = CalendarAnnouncement
        fields = [
            'text'
        ]

class ApptOutcomeForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'outcome',
            'dog',
        ]
        labels = {
            'dog': 'Chosen Dog',
        }

class TimeslotModelFormPrefilled(forms.ModelForm):
    # appointments = forms.ModelMultipleChoiceField(queryset = AppointmentTemplate.objects.all(), required=False)

    class Meta:
        model = Timeslot
        fields = [
            'date',
            'time',
            'appointments',
        ]
        widgets = {
            'date': forms.HiddenInput(),
            #'time': TimePickerWidget(format='%-I:%M%p'),
            'appointments': forms.MultipleHiddenInput(),
        }

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
