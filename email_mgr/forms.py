from django import forms
from .models import EmailTemplate
from tinymce.widgets import TinyMCE

class EmailTemplateForm(forms.ModelForm):

    text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = EmailTemplate
        fields = [
            'text',
            # 'file1',
            # 'file2',
        ]
        labels = {
        #     'file1': 'Upload a file:',
        #     'file2': 'Upload a file:',
        }

class EmailTemplateAddForm(forms.ModelForm):

    text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = EmailTemplate
        fields = [
            'template_name',
            'description',
            'text',
        ]
        labels = {
        }
