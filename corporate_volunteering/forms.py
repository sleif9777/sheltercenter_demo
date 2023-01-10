from django import forms
from tinymce.widgets import TinyMCE

from .models import Organization

class AddOrganizationForm(forms.ModelForm):
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
        super(AddOrganizationForm, self).__init__(*args, **kwargs)
        self.fields['auth_code'].disabled = True
