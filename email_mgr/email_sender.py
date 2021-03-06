import smtplib, ssl, datetime, time, os, mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from appt_calendar.models import Appointment
from appt_calendar.date_time_strings import *
from io import StringIO
from html.parser import HTMLParser
from .email_sender import *
from .models import EmailTemplate
from .dictionary import *
from django.core.mail import EmailMultiAlternatives
from mimetypes import guess_type
from os.path import basename


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


def strip_tags(html, adopter, appt):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def send_email(text, html, reply_to_email, subject, receiver_email, files):
    sender_email = os.environ.get('EMAIL_ADDRESS')
    password = os.environ.get('EMAIL_PASSWORD')

    if reply_to_email == "default":
        reply_to_email = "adoptions@savinggracenc.org"

    email = EmailMultiAlternatives(
        subject,
        text,
        sender_email,
        [receiver_email],
        reply_to = [reply_to_email]
    )

    if "is ready to come home!" in subject:
        email.to += ["adoptions@savinggracenc.org"]

    email.attach_alternative(html, 'text/html')

    file_count = 0

    try:
        for file in files:
            file.open()
            email.attach(basename(file.name), file.read(), guess_type(file.name)[0])
            file.close()
    except:
        pass

    email.send()


def clean_time_and_date(time, date):
    time = time_str(time)
    date = date_no_year_str(date)

    return time, date


def scrub_and_send(subject, template, adopter, appt):
    email = adopter.primary_email
    html = replacer(template.text, adopter, appt)
    files = [template.file1, template.file2]
    text = strip_tags(html, adopter, appt)

    send_email(text, html, "default", subject, email, files)


def alert_date_set(adopter, date):
    subject = "We'll Be In Touch Soon!"
    name = adopter.f_name
    email = adopter.primary_email

    date_string = date_str(date)

    text = """\
    Hi """ + name + """,\n
    We will automatically email you when accepting adoption appointments for """ + date_string + """.\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    """

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>We will automatically email you when accepting adoption appointments for """ + date_string + """.</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email, None)


def upload_errors(errors):
    subject = "Some Adopters Were Not Uploaded"

    pending_errors_text = ""
    blocked_errors_text = ""

    for e in errors:
        if e.status == "2":
            blocked_errors_text += "{0} - {1}\n".format(e.full_name(), "Blocked")
        else:
            pending_errors_text += "{0} - {1}\n".format(e.full_name(), "Pending")

    pending_errors_html = pending_errors_text.replace("\n", "<br>")
    blocked_errors_html = blocked_errors_text.replace("\n", "<br>")

    text = """
        The following applicants have a status of Blocked. They may have been previously blocklisted, and their application may have been approved in error. Please review and adjust their status to Approved manually if neccessary:\n
        {0}
        \n
        The following applicants have a status of Pending:
        {1}
        """.format(blocked_errors_text, pending_errors_text)

    html = """
        <html>
        <body>
        <p>The following applicants have a status of Blocked. They may have been previously blocklisted, and their application may have been approved in error. Please review and adjust their status to Approved manually if neccessary:</p>
        {0}
        <p>The following applicants have a status of Pending:</p>
        {1}
        </body>
        </html>
        """.format(blocked_errors_html, pending_errors_html)

    send_email(text, html, "default", subject, get_base_email(), None) #done

def dates_are_open(adopter, date):
    subject = "Let's Book Your Saving Grace Adoption Appointment! ({0})".format(adopter.full_name().upper())
    name = adopter.f_name
    email = adopter.primary_email

    plain_url = 'http://sheltercenter.dog/' + str(date.day) + '/'
    url = '<a href="http://sheltercenter.dog/">Click here to schedule your appointment.</a>'

    date_string = date_str(date)

    text = """\
    Hi {0},\n
    We are now scheduling adoption appointments for {1}.\n
    Please visit sheltercenter.dog to book an appointment. Your authorization code is {2}.\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    """.format(name, date_string, adopter.auth_code)

    html = """\
    <html>
      <body>
        <p>Hi {0},</p>
        <p>We are now scheduling adoption appointments for {1}.</p>
        <p>Please visit sheltercenter.dog to book an appointment. Your authorization code is {2}.</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """.format(name, date_string, adopter.auth_code)

    send_email(text, html, "default", subject, email, None)

def new_contact_adopter_msg(adopter, message, files, subject):
    if subject == None:
        subject = "New message from the Saving Grace adoptions team"

    name = adopter.f_name
    email = adopter.primary_email

    text = strip_tags(message, adopter, None)

    send_email(text, message, "default", subject, email, files)

def new_contact_us_msg(adopter, message):
    subject = "New message from " + adopter.full_name()
    reply_to = adopter.primary_email

    text = """\
    Adopter: """ + adopter.full_name() + """\n
    \n""" + message

    html = """\
    <html>
      <body>
        <h2>New Message from """ + adopter.full_name() + """</h2>
        <p><b>Message:</b> """ + message + """</p>
      </body>
    </html>
    """

    send_email(text, html, reply_to, subject, get_base_email(), None)

def questions_msg(adopter, appt, questions):
    subject = "Question from " + adopter.full_name()
    reply_to = adopter.primary_email

    text = """\
    Adopter: {0}\n\n
    Appointment: {1}\n\n
    Questions: {2}""".format(adopter.full_name(), appt.date_and_time_string(), questions)

    html = """\
    <html>
      <body>
        <h2>Question from {0}</h2>
        <p><b>Appointment:</b> {1}</p>
        <p><b>Question:</b> {2}</p>
      </body>
    </html>
    """.format(adopter.full_name(), appt.date_and_time_string(), questions)

    send_email(text, html, reply_to, subject, get_base_email(), None)

def confirm_etemp(adopter, appt):
    if appt.appt_type in ["1", "2", "3"]:
        subject = "Your appointment has been confirmed: " + adopter.full_name().upper()
        template = EmailTemplate.objects.get(template_name="Appointment Confirmation")
        scrub_and_send(subject, template, adopter, appt)
    elif appt.appt_type in ["4", "5", "6", "7"]:
        adopter.has_current_appt = False
        adopter.save()

def adoption_paperwork(adopter, appt, hw_status):
    if hw_status == False:
        subject = "Your final adoption appointment has been confirmed: " + adopter.full_name().upper()
    else:
        subject = "Your FTA appointment has been confirmed: " + adopter.full_name().upper()

    template = EmailTemplate.objects.get(template_name="Paperwork Appointment")

    scrub_and_send(subject, template, adopter, appt)

def cancel(adopter, appt):
    subject = "Your appointment has been cancelled"
    template = EmailTemplate.objects.get(template_name="Cancel Appointment")

    scrub_and_send(subject, template, adopter, appt)

def reschedule(adopter, appt):
    subject = "Your appointment has been rescheduled: " + adopter.full_name().upper()
    template = EmailTemplate.objects.get(template_name="Appointment Rescheduled")

    scrub_and_send(subject, template, adopter, appt)

def greeter_reschedule_email(adopter, appt):
    subject = "Your follow-up appointment has been scheduled: " + adopter.full_name().upper()
    template = EmailTemplate.objects.get(template_name="Greeter Reschedule")

    scrub_and_send(subject, template, adopter, appt)

def duplicate_app(adopter):
    invite(adopter)
    # subject = "We already have you in our database: " + adopter.full_name().upper()
    # template = EmailTemplate.objects.get(template_name="Duplicate Application")
    #
    # scrub_and_send(subject, template, adopter, None)

def follow_up(adopter):
    subject = "Thank you for visiting: " + adopter.full_name().upper()
    template = EmailTemplate.objects.get(template_name="Follow-Up (No Host Weekend Information)")

    scrub_and_send(subject, template, adopter, None)

def follow_up_w_host(adopter):
    subject = "Thank you for visiting: " + adopter.full_name().upper()
    template = EmailTemplate.objects.get(template_name="Follow-Up (Host Weekend Information)")

    scrub_and_send(subject, template, adopter, None)

def invite(adopter):
    subject = "Your adoption request has been reviewed: {0}".format(adopter.full_name().upper())

    if adopter.app_interest not in ["", "dogs", "Dogs", "dog", "Dog"] and len(adopter.app_interest) <= 10:
        subject += " ({0})".format(adopter.app_interest)

    template = EmailTemplate.objects.get(template_name="Application Accepted (inside NC, VA, SC)")

    scrub_and_send(subject, template, adopter, None)

def inactive_invite(adopter):
    subject = "Are you ready to schedule your appointment?"
    template = EmailTemplate.objects.get(template_name="Are you ready to schedule your appointment?")

    scrub_and_send(subject, template, adopter, None)

def invite_oos_etemp(adopter):
    subject = "Your adoption request has been reviewed: {0}".format(adopter.full_name().upper())

    if adopter.app_interest not in ["", "dogs", "Dogs", "dog", "Dog"]:
        subject += " ({0})".format(adopter.app_interest)

    template = EmailTemplate.objects.get(template_name="Application Accepted (outside NC, VA, SC)")

    scrub_and_send(subject, template, adopter, None)

def carryover_temp(adopter):
    subject = "Saving Grace Scheduling Update: " + adopter.full_name().upper()
    template = EmailTemplate.objects.get(template_name="Invitation to ShelterCenter (Already in Shelterluv)")

    scrub_and_send(subject, template, adopter, None)

def chosen(adopter, appt):
    subject = "Congratulations on choosing {0}!".format(appt.dog)
    template = EmailTemplate.objects.get(template_name="Chosen Dog")

    scrub_and_send(subject, template, adopter, appt)

def notify_adoptions_cancel(appt, adopter):
    # subject = "UPDATE FOR TODAY'S SCHEDULE"
    subject = "CANCEL: {0} {1}".format(adopter.full_name().upper(), time_str(appt.time))
    text = "Did not reschedule"
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)

def notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt):
    subject = "CANCEL: {0} {1}".format(adopter.full_name().upper(), time_str(current_appt.time))
    text = "Rescheduled for {0} at {1}".format(date_str(new_appt.date), time_str(new_appt.time))
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)

def is_today_or_tomorrow(appt):
    if appt.date == datetime.date.today():
        return "today"

    return "tomorrow"

def get_base_email():
    if str(os.environ.get("DJANGO_ALLOWED_HOST")) != "*":
        return "sheltercenterdev@gmail.com"
    else:
        return "adoptions@savinggracenc.org"

def notify_adoptions_time_change(adopter, current_appt, new_appt):
    subject = "MOVED: {0} NOW AT {1}".format(adopter.full_name().upper(), time_str(new_appt.time))
    text = "Moved from {0}".format(time_str(current_appt.time))
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)

def notify_adoptions_paperwork(adopter, appt):
    if appt.heartworm:
        fta = " FTA"
    else:
        fta = ""

    subject = "PAPERWORK{0}: {1} {2}".format(fta, appt.dog.upper(), time_str(appt.time))
    text = ""
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)

def return_shelterluv(adopter):
    if adopter.application_id:
        text = "https://www.shelterluv.com/adoption_request_print/{0}".format(adopter.application_id)
    else:
        text = "Please print from Shelterluv"

    return text

def notify_adoptions_reschedule_add(adopter, current_appt, new_appt):
    subject = "ADD: {0} {1}".format(adopter.full_name().upper(), time_str(new_appt.time))
    text = "Rescheduled for {0} at {1} | https://www.shelterluv.com/adoption_request_print/{2}".format(is_today_or_tomorrow(new_appt), time_str(new_appt.time), return_shelterluv(adopter))
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)

def notify_adoptions_add(adopter, appt):
    subject = "ADD: {0} {1}".format(adopter.full_name().upper(), time_str(appt.time))
    text = return_shelterluv(adopter)

    html = text

    send_email(text, html, "default", subject, get_base_email(), None)
