from django.shortcuts import render, get_object_or_404, redirect
import datetime, time
from .forms import *
from io import StringIO
from html.parser import HTMLParser
from .email_sender import *
from dashboard.decorators import *

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def email_home(request):

    e_templates = EmailTemplate.objects.all()

    context = {
        'e_templates': e_templates,
        'role': 'admin',
        'page_title': "Email Templates",
    }

    return render(request, "email_mgr/email_home.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_template(request, template_id):
    e_template = EmailTemplate.objects.get(pk=template_id)
    form = EmailTemplateForm(request.POST or None, instance=e_template)
    if form.is_valid():
        form.save()
        return redirect('email_home')
    else:
        form = EmailTemplateForm(request.POST or None, instance=e_template)

    context = {
        'form': form,
        'e_template': e_template,
        'role': 'admin',
        'page_title': "Edit Email Template",
    }

    return render(request, "email_mgr/add_template.html", context)

@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def add_email_template(request):

    form = EmailTemplateForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data

        new_template = EmailTemplate.objects.create(template_name = data['template_name'], text = data['text'])

        return redirect('email_home')
    else:
        form = EmailTemplateForm(request.POST or None)

    context = {
        'form': form,
        'role': 'admin',
        'page_title': "Add Email Template",
    }

    return render(request, "email_mgr/add_template.html/", context)
