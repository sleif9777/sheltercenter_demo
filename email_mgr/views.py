from django.shortcuts import redirect, render
from html.parser import HTMLParser
from io import StringIO

from .email_sender import *
from .forms import *
from .models import *
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
    templates = EmailTemplate.objects.filter(active=True)

    print([template.template_name for template in templates])
    context = {
        'page_title': "Email Templates",
        'templates': templates,
    }

    return render(request, "email_mgr/email_home.html/", context)


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def outbox(request):
    pending_messages = PendingMessage.objects.all()
    context = {
        'page_title': "Outbox",
        'pending_messages': pending_messages,
    }

    return render(request, "email_mgr/outbox.html/", context)


def prepare_pending_message(pm, receiver_email, sender_email):
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message['Reply-To'] = "adoptions@savinggracenc.org"
    message['Subject'] = pm.subject

    part1 = MIMEText(pm.text, "plain")
    part2 = MIMEText(pm.html, "html")
    message.attach(part1)
    message.attach(part2)

    return message


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def send_outbox(request):
    context = ssl.create_default_context()
    password = os.environ.get('EMAIL_PASSWORD')
    pending_messages = list(PendingMessage.objects.all())
    sender_email = os.environ.get('EMAIL_ADDRESS')

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)

        for pm in pending_messages:
            receiver_email = pm.email
            message = prepare_pending_message(
                pm, receiver_email, server, sender_email)
            server.sendmail(sender_email, receiver_email, message.as_string())
            pm.delete()

    context = {
        'pending_messages': pending_messages,
    }

    return redirect('add_adopter')


@authenticated_user
@allowed_users(allowed_roles={'admin', 'superuser'})
def edit_template(request, template_id):
    template = EmailTemplate.objects.get(pk=template_id)
    form = EmailTemplateForm(request.POST or None, instance=template)

    if form.is_valid():
        form.save()
        return redirect('email_home')
    else:
        form = EmailTemplateForm(request.POST or None, instance=template)

    context = {
        'e_template': template,
        'form': form,
        'page_title': "Edit Email Template",
        'role': 'admin',
    }

    return render(request, "email_mgr/add_template.html", context)


@authenticated_user
@allowed_users(allowed_roles={'superuser'})
def add_email_template(request):
    form = EmailTemplateAddForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data
        EmailTemplate.objects.create(
            template_name=data['template_name'],
            text=data['text']
        )

        return redirect('email_home')
    else:
        form = EmailTemplateAddForm(request.POST or None)

    context = {
        'form': form,
        'page_title': "Add Email Template",
        'role': 'admin',
    }

    return render(request, "email_mgr/add_template.html/", context)
