import datetime

from django import forms

from .models import *
from adopter.models import Adopter
from demo import settings as settings

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

class AppointmentModelFormPrefilledEdit(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'date',
            'time',
            'appt_type',
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
        super(AppointmentModelFormPrefilledEdit, self).__init__(*args, **kwargs)

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
            'adopter_notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'adopter_notes': "",
            'bringing_dog': "I plan to bring my dog with me: ",
            'has_cat': "I need a cat-friendly dog: ",
            'mobility': "I would like to request mobility accomodations: "
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(BookAppointmentForm, self).__init__(*args, **kwargs)

class EditAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'adopter_notes',
            'bringing_dog',
            'has_cat',
            'mobility'
        ]
        widgets = {
            'adopter_notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'adopter_notes': "",
            'bringing_dog': "I plan to bring my dog with me: ",
            'has_cat': "I need a cat-friendly dog: ",
            'mobility': "I would like to request mobility accomodations: "
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(EditAppointmentForm, self).__init__(*args, **kwargs)


class AppointmentCheckInForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'adopter_description',
            'counselor'
        ]
        labels = {
            'adopter_description': "Enter a short visual description of the adopter: ",
            'counselor': "Assign a counselor: ",
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(AppointmentCheckInForm, self).__init__(*args, **kwargs)


class JumpToDateForm(forms.Form):
    date = forms.DateField(widget = forms.SelectDateWidget())


class SurrenderForm(forms.Form):
    sg_name = forms.CharField(
        label="Name of pet while at Saving Grace"
    )
    pet_name = forms.CharField(
        required=False,
        label="Current name of pet (if renamed)"
    )
    microchip = forms.CharField(
        label="Microchip #"
    )
    adoption_date = forms.CharField(
        label="Date of adoption"
    )
    reason_for_return = forms.CharField(
        label="Why are you surrendering this dog? Please give as much detail as possible so we can know how to best help",
        widget=forms.Textarea
    )
    utd_vet_records = forms.CharField(
        label="Is your dog up to date on all vet records?",
        widget=forms.Textarea
    )
    sought_training = forms.CharField(
        label="Did you seek training or professional guidance with your dog?",
        widget=forms.Textarea
    )
    aggression_hx = forms.CharField(
        label="Please explain if there have been any aggression concerns towards people or other dogs",
        widget=forms.Textarea
    )
    observations = forms.CharField(
        label="Please share your observations of your dog that will help us determine if they will be successful in our program once again",
        widget=forms.Textarea
    )
    ideal_adopter = forms.CharField(
        label="What type of adopter do you believe would serve your dog best?",
        widget=forms.Textarea
    )

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
