import datetime
import os
import mimetypes
import smtplib
import ssl
import time

from django.core.mail import EmailMultiAlternatives
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html.parser import HTMLParser
from io import StringIO
from mimetypes import guess_type
from os.path import basename

from appt_calendar.models import Appointment
from appt_calendar.date_time_strings import *
from .email_sender import *
from .dictionary import *
from .models import EmailTemplate


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


def send_email(text, html, reply_to_email, subject, receiver_email, files):
    sender_email = os.environ.get('EMAIL_ADDRESS')

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


def scrub_and_send(subject, template, adopter, appt, org=None, event=None):
    email = adopter.primary_email
    html = replacer(template.text, adopter, appt, org, event)
    files = [template.file1, template.file2]
    text = strip_tags(html)

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

    send_email(text, html, "default", subject, get_base_email(), None)
    

def dates_are_open(adopter, date):
    subject = "Let's Book Your Saving Grace Adoption Appointment! ({0})".format(upper_full_name(adopter))
    name = adopter.f_name
    email = adopter.primary_email
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


def confirm_access_request(adopter):
    name = adopter.f_name
    subject = "You have requested calendar access"
    email = adopter.primary_email

    text = """\
    Hi {0},\n
    We have received your request to restore your calendar access and will notify you once ready.\n
    Thank you for choosing to come back to Saving Grace. We look forward to helping you find a new family member soon!\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    """.format(name)

    html = """\
    <html>
      <body>
        <p>Hi {0},</p>
        <p>We have received your request to restore your calendar access and will notify you once ready.</p>
        <p>Thank you for choosing to come back to Saving Grace. We look forward to helping you find a new family member soon!</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """.format(name)

    send_email(text, html, "default", subject, email, None)


def access_requested(adopter):
    name = adopter.f_name
    subject = "{0} has requested calendar access".format(name)
    full_name = adopter.full_name()

    plain_url = 'http://sheltercenter.dog/calendar/allow_access/adopter/{0}/'.format(adopter.id)
    url = '<a target="_blank" href="http://sheltercenter.dog/calendar/allow_access/adopter/{0}/">Click here to grant calendar access.</a>'.format(adopter.id)

    text = """\
    {0} would like to return to adopt again.\n
    Copy and paste this URL to grant access: {1}\n
    Ignore if access should not be granted.
    """.format(full_name, plain_url)

    html = """\
    <html>
      <body>
        <p>{0} would like to return to adopt again.</p>
        <p>{1}</p>
        <p>Ignore if access should not be granted (i.e. shitlisted).</p>
      </body>
    </html>
    """.format(full_name, url)

    send_email(text, html, "default", subject, get_base_email(), None)


def access_restored(adopter):
    subject = "Let's Book Your Saving Grace Adoption Appointment! ({0})".format(upper_full_name(adopter))
    name = adopter.f_name
    email = adopter.primary_email

    text = """\
    Hi {0},\n
    Saving Grace has restored your calendar access and looks forward to helping you find another furry friend to join your family!\n
    Please visit www.sheltercenter.dog to book an appointment. Your authorization code is {1}.\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    """.format(name, adopter.auth_code)

    html = """\
    <html>
      <body>
        <p>Hi {0},</p>
        <p>Saving Grace has restored your calendar access and looks forward to helping you find another furry friend to join your family!</p>
        <p>Please visit www.sheltercenter.dog to book an appointment. Your authorization code is {1}.</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """.format(name, adopter.auth_code)

    send_email(text, html, "default", subject, email, None)


def surrender_emails(adopter, data):
    name = adopter.full_name()
    subject = "Surrender Request from {0}".format(name)
    email = adopter.primary_email

    text = """\
    Hi {0},\n
    Saving Grace has received your surrender request. We are sorry to hear you cannot continue your commitment to {1} (fka {2}).\n
    An adoptions manager will be in touch with you for follow-up soon.\n
    Please do not come to Saving Grace until a set time and date have been determined. We need to ensure we have sufficient space and resources to re-acclimate your dog. As a result, we cannot accept any walk-in surrenders. You MUST have an scheduled appointment.\n
    All the best, \n
    The Adoptions Team\n
    Saving Grace Animals for Adoption\n\n

    Adopter Name: {3}\n
    Dog's Saving Grace Name: {2}\n
    Dog's Current Name: {1}\n
    Microchip #: {4}\n
    Date of Adoption: {5}
    Reason for Surrender: {6}\n
    Is your dog up to date on all vet records?: {7}\n
    Did you seek training or professional guidance with your dog?: {8}\n
    Please explain if there have been any aggression concerns towards people or other dogs?: {9}\n
    Please share your observations of your dog that will help us determine if they will be successful in our program once again: {10}\n
    What type of adopter do you feel would serve your dog best?: {11}\n
    """.format(adopter.f_name, data['pet_name'], data['sg_name'], name, data['microchip'], data['adoption_date'], data['reason_for_return'], data['utd_vet_records'], data['sought_training'], data['aggression_hx'], data['observations'], data['ideal_adopter'])

    html = """\
    Hi {0},<br><br>
    Saving Grace has received your surrender request. We are sorry to hear you cannot continue your commitment to {1} (aka {2}).<br><br>
    An adoptions manager will be in touch with you for follow-up soon. Please do not come to Saving Grace until a set time and date have been determined. We need to ensure we have sufficient space and resources to re-acclimate your dog. As a result, we cannot accept any walk-in surrenders. You MUST have an scheduled appointment.<br><br>
    All the best, <br>
    The Adoptions Team<br>
    Saving Grace Animals for Adoption<br><br>

    <b>Adopter Name:</b> {3}<br>
    <b>Dog's Saving Grace Name:</b> {2}<br>
    <b>Dog's Current Name:</b> {1}<br>
    <b>Microchip #:</b> {4}<br>
    <b>Date of Adoption:</b> {5}<br>
    <b>Reason for Surrender:</b> {6}<br>
    <b>Is your dog up to date on all vet records?:</b> {7}<br>
    <b>Did you seek training or professional guidance with your dog?:</b> {8}<br>
    <b>Please explain if there have been any aggression concerns towards people or other dogs?:</b> {9}<br>
    <b>Please share your observations of your dog that will help us determine if they will be successful in our program once again:</b> {10}<br>
    <b>What type of adopter do you feel would serve your dog best?:</b> {11}<br>
    """.format(adopter.f_name, data['sg_name'], data['pet_name'], name, data['microchip'], data['adoption_date'], data['reason_for_return'], data['utd_vet_records'], data['sought_training'], data['aggression_hx'], data['observations'], data['ideal_adopter'])

    send_email(text, html, "default", subject, email, None)
    send_email(text, html, email, subject, get_base_email(), None)


def new_contact_adopter_msg(adopter, message, files, subject):
    if not subject:
        subject = "New message from the Saving Grace adoptions team"

    email = adopter.primary_email
    text = strip_tags(message)

    send_email(text, message, "default", subject, email, files)


def new_contact_org_msg(organization, message, files, subject):
    if not subject:
        subject = "New message from the Saving Grace volunteering team"

    print(organization, organization.contact_email)

    email = str(organization.contact_email)
    text = strip_tags(message)

    print(type(email), email)

    send_email(text, message, "default", subject, email, files)


def new_contact_us_msg(adopter, message, appt_id=None):
    full_name = adopter.full_name()
    subject = "New message from " + full_name
    reply_to = adopter.primary_email

    if appt_id:
        appt = Appointment.objects.get(pk=appt_id)
        req_appt_str = "<p><b>Requested Appointment:</b> {0}</p>".format(appt.date_and_time_string())
        appt_requested(adopter, appt)
    else:
        req_appt_str = "<em>This adopter is already approved and uploaded to ShelterCenter.</em>"

    text = """\
    Adopter: """ + full_name + """\n
    \n""" + message

    html = """\
    <html>
      <body>
        <h2>New Message from {0}</h2>
        {1}<br>
        <p><b>Message:</b> {2}</p>
      </body>
    </html>
    """.format(full_name, req_appt_str, message)

    send_email(text, html, reply_to, subject, get_base_email(), None)


def new_contact_volunteer_event_team_msg(org, message, event=None):
    org_name = org.org_name
    leader_name = org.leader_name()
    subject = "New message from {0}".format(org_name)
    reply_to = org.contact_email

    text = """\
    Organization: """ + org_name + """\n
    \n""" + message

    html = """\
    <html>
      <body>
        <h2>New Message from {0} ({1})</h2>
        <p><b>Message:</b> {2}</p>
      </body>
    </html>
    """.format(leader_name, org_name, message)

    send_email(text, html, reply_to, subject, get_events_email(), None)


def event_booked(org, event):
    org_name = org.org_name
    leader_fname = org.leader_fname
    subject = "New event from {0}".format(org_name)
    email = org.contact_email

    external_text = "Hi {0} and the rest of the {1} team! Thank you for choosing {2} as your upcoming Day of Service. Our coordinators will follow up with you closer to your event date.".format(
        leader_fname, org_name, event.date_string())

    internal_text = "{0} has chosen {1} as for their Days of Service event! Reply directly to this email to start planning with {2}.".format(
        org_name, event.date_string(), leader_fname)

    external_html = """\
    <html>
      <body>
        <p>Hi {0} and the rest of the {1} team!</p>
        <p>Thank you for choosing {2} as your upcoming Day of Service. Our coordinators will follow up with you closer to your event date.</p>
      </body>
    </html>
    """.format(leader_fname, org_name, event.date_string())

    internal_html = """\
    <html>
      <body>
        <p>{0} has chosen {1} as for their Days of Service event! Reply directly to this email to start planning with {2}.</p>
      </body>
    </html>
    """.format(org_name, event.date_string(), leader_fname)

    #send email to org
    send_email(external_text, external_html, get_events_email(), subject, email, None)
    #send email to margaret and team
    send_email(internal_text, internal_html, email, subject, get_events_email(), None)


def appt_requested(adopter, appt):
    subject = "You Have Requested An Appointment"
    name = adopter.f_name
    email = adopter.primary_email

    text = """\
    Hi {0},\n
    You have requested an appointment for {1}. This is not a confirmation, please do not plan to come until we have followed up. We will follow up as soon as we see your message.\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    """.format(name, appt.date_and_time_string())

    html = """\
    <html>
      <body>
        <p>Hi {0},</p>
        <p>You have requested an appointment for {1}. <b>This is not a confirmation, please do not plan to come until we have followed up.</b> We will follow-up within 24 hours.</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """.format(name, appt.date_and_time_string())

    send_email(text, html, "default", subject, email, None)


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
    if appt.schedulable():
        subject = "Your appointment has been confirmed: " + upper_full_name(adopter)
        template = EmailTemplate.objects.get(template_name="Appointment Confirmation")
        scrub_and_send(subject, template, adopter, appt)
    else:
        adopter.has_current_appt = False
        adopter.save()


def adoption_paperwork(adopter, appt, hw_status):
    if not hw_status:
        subject = "Your final adoption appointment has been confirmed: " + upper_full_name(adopter)
    else:
        subject = "Your FTA appointment has been confirmed: " + upper_full_name(adopter)

    template = EmailTemplate.objects.get(template_name="Paperwork Appointment")
    scrub_and_send(subject, template, adopter, appt)


def cancel(adopter, appt):
    subject = "Your appointment has been cancelled"
    template = EmailTemplate.objects.get(template_name="Cancel Appointment")

    scrub_and_send(subject, template, adopter, appt)


def reschedule(adopter, appt):
    subject = "Your appointment has been rescheduled: " + upper_full_name(adopter)
    template = EmailTemplate.objects.get(template_name="Appointment Rescheduled")

    scrub_and_send(subject, template, adopter, appt)


def greeter_reschedule_email(adopter, appt):
    subject = "Your follow-up appointment has been scheduled: " + upper_full_name(adopter)
    template = EmailTemplate.objects.get(template_name="Appointment Confirmation")

    scrub_and_send(subject, template, adopter, appt)


def duplicate_app(adopter):
    invite(adopter)


def follow_up(adopter):
    subject = "Thank you for visiting: " + upper_full_name(adopter)
    template = EmailTemplate.objects.get(template_name="Follow-Up (No Host Weekend Information)")

    scrub_and_send(subject, template, adopter, None)


def follow_up_w_host(adopter):
    subject = "Thank you for visiting: " + upper_full_name(adopter)
    template = EmailTemplate.objects.get(template_name="Follow-Up (Host Weekend Information)")

    scrub_and_send(subject, template, adopter, None)


def eval_unique_app_interest(response):
    return response not in ["", "dogs", "Dogs", "dog", "Dog"]


def eval_app_interest(response):
    # evaluates whether app interest should be included in subject line
    unique = eval_unique_app_interest(response)
    short = len(response) >= 10

    return True if unique and short else False


def upper_full_name(adopter):
    return adopter.full_name().upper()


def invite(adopter):
    subject = "Your adoption request has been reviewed: {0}".format(
        upper_full_name(adopter))
    include_app_interest = eval_app_interest(adopter.app_interest)

    if include_app_interest:
        subject += " ({0})".format(adopter.app_interest)

    if adopter.out_of_state:
        template = EmailTemplate.objects.get(
            template_name="Application Accepted (outside NC, VA, SC)")
    else:
        template = EmailTemplate.objects.get(
            template_name="Application Accepted (inside NC, VA, SC)")

    scrub_and_send(subject, template, adopter, None)


def inactive_invite(adopter):
    subject = "Are you ready to schedule your appointment?"
    template = EmailTemplate.objects.get(template_name="Are you ready to schedule your appointment?")

    scrub_and_send(subject, template, adopter, None)


def carryover_temp(adopter):
    subject = "Saving Grace Scheduling Update: " + upper_full_name(adopter)
    template = EmailTemplate.objects.get(template_name="Invitation to ShelterCenter (Already in Shelterluv)")

    scrub_and_send(subject, template, adopter, None)


def chosen(adopter, appt):
    subject = "Congratulations on choosing {0}!".format(appt.dog)
    template = EmailTemplate.objects.get(template_name="Chosen Dog")

    scrub_and_send(subject, template, adopter, appt)


def notify_adoptions_cancel(appt, adopter):
    subject = "CANCEL: {0} {1}".format(upper_full_name(adopter), time_str(appt.time))
    text = "Did not reschedule"
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)


def notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt):
    subject = "CANCEL: {0} {1}".format(upper_full_name(adopter), time_str(current_appt.time))
    text = "Rescheduled for {0} at {1}".format(date_str(new_appt.date), time_str(new_appt.time))
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)


def is_today_or_tomorrow(appt):
    return "today" if appt.date == datetime.date.today() else "tomorrow"


def get_base_email():
    if str(os.environ.get("DJANGO_ALLOWED_HOST")) != "*":
        return "sheltercenterdev@gmail.com"
    else:
        return "adoptions@savinggracenc.org"


def get_events_email():
    if str(os.environ.get("DJANGO_ALLOWED_HOST")) != "*":
        return "sheltercenterdev@gmail.com"
    else:
        return "events@savinggracenc.org"


def notify_adoptions_time_change(adopter, current_appt, new_appt):
    subject = "MOVED: {0} NOW AT {1}".format(
        upper_full_name(adopter), time_str(new_appt.time))
    text = "Moved from {0}".format(time_str(current_appt.time))
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)


def notify_adoptions_paperwork(appt):
    if appt.heartworm:
        fta = " FTA"
    else:
        fta = ""

    subject = "PAPERWORK{0}: {1} {2}".format(
        fta, appt.dog.upper(), time_str(appt.time))
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
    subject = "ADD: {0} {1}".format(upper_full_name(adopter), time_str(new_appt.time))
    text = "Rescheduled for {0} at {1} | https://www.shelterluv.com/adoption_request_print/{2}".format(
        is_today_or_tomorrow(new_appt), time_str(new_appt.time), return_shelterluv(adopter))
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)


def notify_adoptions_add(adopter, appt):
    subject = "ADD: {0} {1}".format(upper_full_name(adopter), time_str(appt.time))
    text = return_shelterluv(adopter)
    html = text

    send_email(text, html, "default", subject, get_base_email(), None)
