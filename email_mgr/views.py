from django.shortcuts import render, get_object_or_404, redirect
import datetime, time
from .forms import *
from .models import *
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
    }

    return render(request, "email_mgr/email_home.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def outbox(request):
    pending_messages = PendingMessage.objects.all()

    context = {
        'pending_messages': pending_messages,
    }

    return render(request, "email_mgr/outbox.html/", context)

@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def send_outbox(request):
    pending_messages = list(PendingMessage.objects.all())

    sender_email = os.environ.get('EMAIL_ADDRESS')
    password = os.environ.get('EMAIL_PASSWORD')

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)

        for pm in pending_messages:
            receiver_email = pm.email
            message = MIMEMultipart("alternative")
            message["From"] = sender_email
            message["To"] = receiver_email
            message['Reply-To'] = "adoptions@savinggracenc.com"
            message['Subject'] = pm.subject

            part1 = MIMEText(pm.text, "plain")
            part2 = MIMEText(pm.html, "html")
            message.attach(part1)
            message.attach(part2)
            server.sendmail(sender_email, receiver_email, message.as_string())
            pm.delete()

    context = {
        'pending_messages': pending_messages,
    }

    return redirect('add_adopter')

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

    form = EmailTemplateAddForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data

        new_template = EmailTemplate.objects.create(template_name = data['template_name'], text = data['text'])

        return redirect('email_home')
    else:
        form = EmailTemplateAddForm(request.POST or None)

    context = {
        'form': form,
        'role': 'admin',
        'page_title': "Add Email Template",
    }

    return render(request, "email_mgr/add_template.html/", context)
