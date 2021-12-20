from django import forms
import datetime
from .models import TimeslotTemplate, AppointmentTemplate

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
