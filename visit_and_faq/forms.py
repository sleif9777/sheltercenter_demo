from django import forms
from .models import *
from tinymce.widgets import TinyMCE

class FAQSectionForm(forms.ModelForm):
    class Meta:
        model = FAQSection
        fields = [
            'name',
            'order',
        ]
        widgets = {

        }
        labels = {
            'name': 'Section Name',
            'order': 'Display Order'
        }

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = [
            'question',
            'answer',
            'order',
        ]
        widgets = {
            'question': forms.TextInput(attrs={'size': 160}),
            'answer': TinyMCE(attrs={'cols': 80, 'rows': 30})
        }
        labels = {
        }
