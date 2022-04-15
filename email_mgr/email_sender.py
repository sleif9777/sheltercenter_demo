import smtplib, ssl, datetime, time, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from appt_calendar.models import Appointment
from appt_calendar.date_time_strings import *
from io import StringIO
from html.parser import HTMLParser
from .email_sender import *
from .models import EmailTemplate
from .dictionary import *

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

# def send_email(text, html, reply_to, subject, receiver_email):
#     sender_email = "savinggracenc@sheltercenter.dog"
#     password = os.environ.get('EMAIL_PASSWORD')
#
#     message = MIMEMultipart("alternative")
#     message["From"] = sender_email
#     message["To"] = receiver_email
#
#     if reply_to == "default":
#         message['Reply-To'] = "adoptions@savinggracenc.org"
#     else:
#         message['Reply-To'] = reply_to
#     message['Subject'] = subject
#
#     part1 = MIMEText(text, "plain")
#     part2 = MIMEText(html, "html")
#     message.attach(part1)
#     message.attach(part2)
#
#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#         server.login(sender_email, password)
#         server.sendmail(
#             sender_email, receiver_email, message.as_string()
#         )

def send_email(text, html, reply_to, subject, receiver_email):
    sender_email = os.environ.get('EMAIL_ADDRESS')
    password = os.environ.get('EMAIL_PASSWORD')

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email

    if reply_to == "default":
        message['Reply-To'] = "adoptions@savinggracenc.com"
    else:
        message['Reply-To'] = reply_to
    message['Subject'] = subject

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def clean_time_and_date(time, date):
    time = time_str(time)
    date = date_no_year_str(date)

    return time, date

def scrub_and_send(subject, template, adopter, appt):
    email = adopter.adopter_email
    html = replacer(template.text, adopter, appt)

    text = strip_tags(html, adopter, appt)

    send_email(text, html, "default", subject, email)

def alert_date_set(adopter, date):
    subject = "We'll Be In Touch Soon!"
    name = adopter.adopter_first_name
    email = adopter.adopter_email

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

    send_email(text, html, "default", subject, email)

def upload_errors(errors):
    subject = "Some Adopters Were Not Uploaded"

    text = "The following applicants have a status of Blocked and were not sent an invitation:"

    html = """\
    <html>
      <body>
      <p>The following applicants have a status of Blocked and were not sent an invitation:</p>
    """

    for e in errors:
        text += e + "\n"
        html += "{0}<br>".format(e)

    html += """\
      </body>
    </html>
    """

    send_email(text, html, "default", subject, "sheltercenterdev@gmail.com")

def dates_are_open(adopter, date):
    subject = "Let's Book Your Saving Grace Adoption Appointment!"
    name = adopter.adopter_first_name
    email = adopter.adopter_email

    plain_url = 'http://sheltercenter.dog/' + str(date.day) + '/'
    url = '<a href="http://sheltercenter.dog/">Click here to schedule your appointment.</a>'

    date_string = date_str(date)

    text = """\
    Hi """ + name + """,\n
    We are now scheduling adoption appointments for """ + date_string + """.\n
    Visit this website to schedule your adoption appointment: """ + url + """\n
    Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    """

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>We are now scheduling adoption appointments for """ + date_string + """.</p>
        <p>""" + url + """</p>
        <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def new_contact_adopter_msg(adopter, message):
    subject = "New message from the Saving Grace adoptions team"
    name = adopter.adopter_first_name
    email = adopter.adopter_email

    text = strip_tags(message, adopter, None)

    send_email(text, message, "default", subject, email)

def new_contact_us_msg(adopter, message):
    subject = "New message from " + adopter.adopter_full_name()
    reply_to = adopter.adopter_email
    email = "sheltercenterdev@gmail.com"

    text = """\
    Adopter: """ + adopter.adopter_full_name() + """\n
    \n""" + message

    html = """\
    <html>
      <body>
        <h2>New Message from """ + adopter.adopter_full_name() + """</h2>
        <p><b>Message:</b> """ + message + """</p>
      </body>
    </html>
    """

    send_email(text, html, reply_to, subject, email)

def confirm_etemp(adopter, appt):
    subject = "Your appointment has been confirmed: " + adopter.adopter_full_name().upper()
    template = EmailTemplate.objects.get(template_name="Appointment Confirmation")

    scrub_and_send(subject, template, adopter, appt)

def adoption_paperwork(adopter, appt, hw_status):
    if hw_status == False:
        subject = "Your final adoption appointment has been confirmed: " + adopter.adopter_full_name().upper()
    else:
        subject = "Your FTA appointment has been confirmed: " + adopter.adopter_full_name().upper()

    template = EmailTemplate.objects.get(template_name="Paperwork Appointment")

    scrub_and_send(subject, template, adopter, appt)

def cancel(adopter, appt):
    subject = "Your appointment has been cancelled"
    template = EmailTemplate.objects.get(template_name="Cancel Appointment")

    scrub_and_send(subject, template, adopter, appt)

def reschedule(adopter, appt):
    subject = "Your appointment has been rescheduled: " + adopter.adopter_full_name().upper()
    template = EmailTemplate.objects.get(template_name="Appointment Rescheduled")

    scrub_and_send(subject, template, adopter, appt)

def greeter_reschedule_email(adopter, appt):
    subject = "Your follow-up appointment has been scheduled: " + adopter.adopter_full_name().upper()
    template = EmailTemplate.objects.get(template_name="Greeter Reschedule")

    scrub_and_send(subject, template, adopter, appt)

def duplicate_app(adopter):
    subject = "We already have you in our database: " + adopter.adopter_full_name().upper()
    template = EmailTemplate.objects.get(template_name="Duplicate Application")

    scrub_and_send(subject, template, adopter, None)

def follow_up(adopter):
    subject = "Thank you for visiting: " + adopter.adopter_full_name().upper()
    template = EmailTemplate.objects.get(template_name="Follow-Up (No Host Weekend Information)")

    scrub_and_send(subject, template, adopter, None)

def follow_up_w_host(adopter):
    subject = "Thank you for visiting: " + adopter.adopter_full_name().upper()
    template = EmailTemplate.objects.get(template_name="Follow-Up (Host Weekend Information)")

    scrub_and_send(subject, template, adopter, None)

def invite(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    template = EmailTemplate.objects.get(template_name="Add Adopter (inside NC, VA, SC)")

    scrub_and_send(subject, template, adopter, None)

def inactive_invite(adopter):
    subject = "Are you ready to schedule your appointment?"
    template = EmailTemplate.objects.get(template_name="Are you ready to schedule your appointment?")

    scrub_and_send(subject, template, adopter, None)

def invite_oos_etemp(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    template = EmailTemplate.objects.get(template_name="Add Adopter (outside NC, VA, SC)")

    scrub_and_send(subject, template, adopter, None)

def carryover_temp(adopter):
    subject = "Saving Grace Scheduling Update: " + adopter.adopter_full_name().upper()
    template = EmailTemplate.objects.get(template_name="Invitation to ShelterCenter (Already in Shelterluv)")

    scrub_and_send(subject, template, adopter, None)

def chosen(adopter, appt):
    subject = "Congratulations on choosing " + appt.dog
    template = EmailTemplate.objects.get(template_name="Chosen Dog")

    scrub_and_send(subject, template, adopter, appt)

def notify_adoptions_cancel(appt, adopter):
    subject = "UPDATE FOR TODAY'S SCHEDULE"

    text = """\
{0} has cancelled their {1} appointment today.
""".format(adopter.adopter_full_name(), time_str(appt.time))

    html = """\
    <html>
      <body>
        <p>{0} has cancelled their {1} appointment today.</p>
      </body>
    </html>
    """.format(adopter.adopter_full_name(), time_str(appt.time))

    send_email(text, html, "default", subject, "sheltercenterdev@gmail.com")

def notify_adoptions_reschedule_cancel(adopter, current_appt, new_appt):
    subject = "UPDATE FOR TODAY'S SCHEDULE"

    text = """\
{0} has rescheduled their {1} appointment today for {2} at {3}.\n
The greeter and admin calendars have been updated with this change.
""".format(adopter.adopter_full_name(), time_str(current_appt.time), date_str(new_appt.date), time_str(new_appt.time))

    html = """\
    <html>
      <body>
        <p>{0} has rescheduled their {1} appointment today for {2} at {3}.<br>The greeter and admin calendars have been updated with this change.</p>
      </body>
    </html>
    """.format(adopter.adopter_full_name(), time_str(current_appt.time), date_str(new_appt.date), time_str(new_appt.time))

    send_email(text, html, "default", subject, "sheltercenterdev@gmail.com")

def notify_adoptions_reschedule_add(adopter, current_appt, new_appt):
    subject = "UPDATE FOR TODAY'S SCHEDULE"

    text = """\
{0} has rescheduled their appointment for {1} today.\n
The greeter and admin calendars have been updated with this change. Please print their application from Shelterluv as soon as possible.
""".format(adopter.adopter_full_name(), time_str(new_appt.time))

    html = """\
    <html>
      <body>
        <p>{0} has rescheduled their appointment for {1} today.<br>The greeter and admin calendars have been updated with this change. Please print their application from Shelterluv as soon as possible.</p>
      </body>
    </html>
    """.format(adopter.adopter_full_name(), time_str(new_appt.time))

    send_email(text, html, "default", subject, "sheltercenterdev@gmail.com")

def notify_adoptions_add(adopter, appt):
    subject = "UPDATE FOR TODAY'S SCHEDULE"

    text = """\
{0} has booked their appointment for {1} today.\n
The greeter and admin calendars have been updated with this change. Please print their application from Shelterluv as soon as possible.
""".format(adopter.adopter_full_name(), time_str(appt.time))

    html = """\
    <html>
      <body>
        <p>{0} has booked their appointment for {1} today.<br>The greeter and admin calendars have been updated with this change. Please print their application from Shelterluv as soon as possible.</p>
      </body>
    </html>
    """.format(adopter.adopter_full_name(), time_str(appt.time))

    send_email(text, html, "default", subject, "sheltercenterdev@gmail.com")
