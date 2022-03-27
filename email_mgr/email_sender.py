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

def strip_anchors(html, adopter, appt):
    if os.environ.get('LOCALHOST'):
        base_name = 'localhost'
    else:
        base_name = 'sheltercenter.dog'

    try:
        cancel_url = '<a href="http://{0}/calendar/adopter/cancel/adopter/{1}/appt/{2}/date/{3}/{4}/{5}/">Click here to cancel your appointment.</a>'.format(base_name, adopter.id, appt.id, appt.date.year, appt.date.month, appt.date.day)

        plain_cancel_url = 'http://{0}/calendar/adopter/cancel/adopter/{1}/appt/{2}/date/{3}/{4}/{5}/'.format(base_name, adopter.id, appt.id, appt.date.year, appt.date.month, appt.date.day)

        home_url = '<a href="http://{0}/adopter/{1}/">Click here to schedule your appointment.</a>'.format(base_name, adopter.id)

        plain_home_url = 'http://{0}/adopter/{1}/'.format(base_name, adopter.id)

        html = html.replace(cancel_url, plain_cancel_url)
        html = html.replace(home_url, plain_home_url)
    except:
        pass

    host_url = '<a href="https://savinggracenc.org/host-a-dog/">If you would like to learn more about our Weekend Host program, please visit our website.</a>'
    plain_host_url = 'https://savinggracenc.org/host-a-dog/'

    html = html.replace(host_url, plain_host_url)

    return html

def strip_tags(html, adopter, appt):
    html = strip_anchors(html, adopter, appt)

    s = MLStripper()
    s.feed(html)
    return s.get_data()

def send_email(text, html, reply_to, subject, receiver_email):
    sender_email = "sheltercenterdev@gmail.com"
    password = os.environ.get('EMAIL_PASSWORD')

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email

    if reply_to == "default":
        message['Reply-To'] = "sheltercenterdev@gmail.com"
    else:
        message['Reply-To'] = reply_to
    message['Subject'] = subject

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def clean_time_and_date(time, date):
    time = time_str(time)
    date = date_no_year_str(date)

    return time, date

#def custom_msg(adopter, message, subject):

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

    plain_url = 'http://sheltercenter.dog/calendar/adopter/' + str(adopter.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    url = '<a href="http://sheltercenter.dog/calendar/adopter/' + str(adopter.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Click here to schedule your appointment.</a>'

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

    try:
        appt = Appointment.objects.get(adopter_choice=adopter.id)
        date = appt.date
    except:
        appt = None

    print(appt)

    if appt != None:
        header_appt = appt.date_and_time_string()
        plain_cancel_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
        cancel_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Cancel Appointment</a>'
        plain_reschedule_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
        reschedule_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">Reschedule Appointment</a>'

        text = """\
        Adopter: """ + adopter.adopter_full_name() + """\n
        Current Appointment: """ + header_appt + """\n
        Reschedule Appointment Here: """ + plain_reschedule_url + """\n
        Cancel Appointment Here: """ + plain_cancel_url + """\n
        \n""" + message

        html = """\
        <html>
          <body>
            <h2>New Message from """ + adopter.adopter_full_name() + """</h2>
            <p><b>Current Appointment:</b> """ + header_appt + """</p>
            <p>""" + reschedule_url + """</p>
            <p>""" + cancel_url + """</p>
            <p><b>Message:</b> """ + message + """</p>
          </body>
        </html>
        """
    else:
        header_appt = "None Scheduled"
        plain_schedule_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
        schedule_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">Schedule Appointment</a>'

        text = """\
        Adopter: """ + adopter.adopter_full_name() + """\n
        Current Appointment: """ + header_appt + """\n
        Schedule Appointment Here: """ + plain_schedule_url + """\n
        \n""" + message

        html = """\
        <html>
          <body>
            <h2>New Message from """ + adopter.adopter_full_name() + """</h2>
            <p><b>Current Appointment:</b> """ + header_appt + """</p>
            <p>""" + schedule_url + """</p>
            <p><b>Message:</b> """ + message + """</p>
          </body>
        </html>
        """

    send_email(text, html, reply_to, subject, email)

def confirm_etemp(adopter, appt):
    subject = "Your appointment has been confirmed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    template = EmailTemplate.objects.get(template_name="Appointment Confirmation")

    html = replacer(template.text, adopter, appt)

    text = strip_tags(html, adopter, appt)

    send_email(text, html, "default", subject, email)

def adoption_paperwork(adopter, appt, hw_status):
    if hw_status == False:
        subject = "Your final adoption appointment has been confirmed: " + adopter.adopter_full_name().upper()
    else:
        subject = "Your FTA appointment has been confirmed: " + adopter.adopter_full_name().upper()

    email = adopter.adopter_email
    template = EmailTemplate.objects.get(template_name="Paperwork Appointment")

    html = replacer(template.text, adopter, appt)

    text = strip_tags(html, adopter, appt)

    send_email(text, html, "default", subject, email)

def cancel(adopter, appt):
    subject = "Your appointment has been cancelled"
    email = adopter.adopter_email
    template = EmailTemplate.objects.get(template_name="Cancel Appointment")

    html = replacer(template.text, adopter, appt)

    text = strip_tags(html, adopter, appt)

    send_email(text, html, "default", subject, email)

def reschedule(adopter, appt):
    print("hit it!")
    subject = "Your appointment has been rescheduled: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email

    template = EmailTemplate.objects.get(template_name="Appointment Rescheduled")

    html = replacer(template.text, adopter, appt)

    text = strip_tags(html, adopter, appt)

    send_email(text, html, "default", subject, email)

def greeter_reschedule_email(adopter, appt):
    subject = "Your follow-up appointment has been scheduled: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email

    template = EmailTemplate.objects.get(template_name="Greeter Reschedule")

    html = replacer(template.text, adopter, appt)

    text = strip_tags(html, adopter, appt)

    send_email(text, html, "default", subject, email)

def duplicate_app(adopter):
    subject = "We already have you in our database: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email

    template = EmailTemplate.objects.get(template_name="Duplicate Application")

    html = replacer(template.text, adopter, None)

    text = strip_tags(html, adopter, None)

    send_email(text, html, "default", subject, email)

def follow_up(adopter):
    subject = "Thank you for visiting: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email

    template = EmailTemplate.objects.get(template_name="Follow-Up (No Host Weekend Information)")

    html = replacer(template.text, adopter, None)

    text = strip_tags(html, adopter, None)

    send_email(text, html, "default", subject, email)

def follow_up_w_host(adopter):
    subject = "Thank you for visiting: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email

    template = EmailTemplate.objects.get(template_name="Follow-Up (Host Weekend Information)")

    html = replacer(template.text, adopter, None)

    text = strip_tags(html, adopter, None)

    send_email(text, html, "default", subject, email)

def invite(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email

    template = EmailTemplate.objects.get(template_name="Add Adopter (inside NC, VA, SC)")

    html = replacer(template.text, adopter, None)

    text = strip_tags(html, adopter, None)

    send_email(text, html, "default", subject, email)

def invite_oos_etemp(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    template = EmailTemplate.objects.get(template_name="Add Adopter (outside NC, VA, SC)")

    html = replacer(template.text, adopter, None)

    text = strip_tags(html, adopter, None)

    print(html)
    print(text)

    send_email(text, html, "default", subject, email)

def invite_friends_of_foster_adoption(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    text = """\
Hi """ + name + """,\n
Thank you for your interest and adoption request! It sounds like you have met """ + adopter.chosen_dog + """ at the foster's home, and you are committed to adopting this puppy. Can you confirm that this is the case? If so, we will put you in the reservation tablet to formally adopt """ + adopter.chosen_dog + """ once the vetting is complete.\n
Thank you,
The Adoptions Team\n
Saving Grace Animals for Adoption
"""

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>Thank you for your interest and adoption request! It sounds like you have met """ + adopter.chosen_dog + """ at the foster's home, and you are committed to adopting this puppy. Can you confirm that this is the case? If so, we will put you in the reservation tablet to formally adopt """ + adopter.chosen_dog + """ once the vetting is complete.</p>
        <p>Thank you,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def invite_foster_adoption(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    text = """\
Hi """ + name + """,\n
Thank you for fostering with us! It sounds like you intend to adopt your foster """ + adopter.chosen_dog + """. Can you confirm that this is the case? If so, we will put you in the reservation tablet to formally adopt """ + adopter.chosen_dog + """ once the vetting is complete.\n
Thank you,
The Adoptions Team\n
Saving Grace Animals for Adoption
"""

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>Thank you for fostering with us! It sounds like you intend to adopt your foster """ + adopter.chosen_dog + """. Can you confirm that this is the case? If so, we will put you in the reservation tablet to formally adopt """ + adopter.chosen_dog + """ once the vetting is complete.</p>
        <p>Thank you,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def invite_host_adoption(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    text = """\
Hi """ + name + """,\n
Thank you for your interest, and thank you for hosting with us! We're so glad that """ + adopter.chosen_dog + """ worked out so well for you. """ + adopter.chosen_dog + """, like all our dogs, was pulled from an animal shelter. I'm afraid we do not have much background or history. We wish they could talk!\n
We will be in touch with you about next steps soon!\n
Thank you,
The Adoptions Team\n
Saving Grace Animals for Adoption
"""

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>Thank you for your interest, and thank you for hosting with us! We're so glad that """ + adopter.chosen_dog + """ worked out so well for you. """ + adopter.chosen_dog + """, like all our dogs, was pulled from an animal shelter. I'm afraid we do not have much background or history. We wish they could talk!</p>
        <p>We will be in touch with you about next steps soon!</p>
        <p>Thank you,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

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
