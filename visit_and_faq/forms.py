from django import forms
from tinymce.widgets import TinyMCE

from .models import *

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

class HelpSectionForm(forms.ModelForm):
    class Meta:
        model = HelpSection
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

class HelpTopicForm(forms.ModelForm):
    class Meta:
        model = HelpTopic
        fields = [
            'header',
            'text',
            'order',
        ]
        widgets = {
            'header': forms.TextInput(attrs={'size': 160}),
            'text': TinyMCE(attrs={'cols': 80, 'rows': 30})
        }
        labels = {
        }

class VisitorInstructionForm(forms.ModelForm):
    class Meta:
        model = VisitorInstruction
        fields = [
            'header',
            'text',
            'order',
        ]
        widgets = {
            'header': forms.TextInput(attrs={'size': 160}),
            'text': TinyMCE(attrs={'cols': 80, 'rows': 30})
        }
        labels = {
        }
