from django import forms
from .models import EmailTemplate
from tinymce.widgets import TinyMCE

class EmailTemplateForm(forms.ModelForm):

    text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = EmailTemplate
        fields = [
            'template_name',
            'text',
        ]
        labels = {
        }
