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

    plain_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/' + str(adopter.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/' + str(adopter.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Click here to schedule your appointment.</a>'

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

def limited_matches(adopter, appt, description):
    print(description)
    if description == "lowshed":
        description = "low-shedding and/or hypoallergenic dogs"

    subject = "An update about your Saving Grace appointment"
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    date = appt.date

    plain_reschedule_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    reschedule_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">If you would prefer to reschedule your appointment, click here.</a>'

    plain_cancel_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    cancel_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">If you would prefer to cancel your appointment, click here.</a>'

    if description in ["puppies", "small dogs"]:
        text = """\
        Hi """ + name + """,\n
        We wanted to follow up with you as we see you have requested to meet """ + description + """.\n
        We are a little limited with available """ + description + """ at this time.\n
        We do encourage you to keep your appointment. There are always wonderful dogs for you to visit with and we always recommend keeping an open mind to see who may click with you. We also have dogs who have not had the chance to have photos taken and are not on our website yet.\n
        If you wish to reschedule your appointment, you can do so here: """ + plain_reschedule_url + """\n
        If you wish to cancel your appointment, you can do so here: """ + plain_cancel_url + """\n
        Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.\n
        All the best, \n
        The Adoptions Team
        Saving Grace Animals for Adoption
        """

        html = """\
        <html>
          <body>
            <h2>An Update For Your Saving Grace Appointment</h2>
            <p>Hi """ + name + """,</p>
            <p>We wanted to follow up with you as we see you have requested to meet """ + description + """.</p>
            <p>We are a little limited with available """ + description + """ at this time.</p>
            <p>We do encourage you to keep your appointment. There are always wonderful dogs for you to visit with and we always recommend keeping an open mind to see who may click with you. We also have dogs who have not had the chance to have photos taken and are not on our website yet.</p>
            <p>""" + reschedule_url + """</p>
            <p>""" + cancel_url + """</p>
            <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.</p>
            <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
          </body>
        </html>
        """
    elif description in ["low-shedding and/or hypoallergenic dogs"]:
        text = """\
        Hi """ + name + """,\n
        We wanted to follow up with you as we see you have requested to meet """ + description + """.\n
        We are a little limited with available """ + description + """ at this time. These types of dogs are very popular and do not come into our program often. When they do, they do find homes rather quickly.\n
        We do encourage you to keep your appointment. There are always wonderful dogs for you to visit with and we always recommend keeping an open mind to see who may click with you. We also have dogs who have not had the chance to have photos taken and are not on our website yet.\n
        If you wish to reschedule your appointment, you can do so here: """ + plain_reschedule_url + """\n
        If you wish to cancel your appointment, you can do so here: """ + plain_cancel_url + """\n
        Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.\n
        All the best, \n
        The Adoptions Team
        Saving Grace Animals for Adoption
        """

        html = """\
        <html>
          <body>
            <h2>An Update For Your Saving Grace Appointment</h2>
            <p>Hi """ + name + """,</p>
            <p>We wanted to follow up with you as we see you have requested to meet """ + description + """</p>
            <p>We are a little limited with available """ + description + """ at this time. These types of dogs are very popular and do not come into our program often. When they do, they do find homes rather quickly.</p>
            <p>We do encourage you to keep your appointment. There are always wonderful dogs for you to visit with and we always recommend keeping an open mind to see who may click with you. We also have dogs who have not had the chance to have photos taken and are not on our website yet.</p>
            <p>""" + reschedule_url + """</p>
            <p>""" + cancel_url + """</p>
            <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.</p>
            <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
          </body>
        </html>
        """
    else:
        text = """\
        Hi """ + name + """,\n
        We wanted to follow up as we see the following notes you provided for your upcoming appointment:\n""" + appt.adopter_notes + """\n
        We are a little limited with dogs matching that description at this time.\n
        While your first choices may no longer be available, we do encourage you to keep your appointment. We always have wonderful dogs for you to visit with and always recommend keeping an open mind to see who may click with you. Many adopters end up adopting a totally different dog than the one they come to meet. We also have dogs who have not had the chance to have photos taken and are not on our website yet.\n
        If you wish to reschedule your appointment, you can do so here: """ + plain_reschedule_url + """\n
        If you wish to cancel your appointment, you can do so here: """ + plain_cancel_url + """\n
        Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.\n
        All the best, \n
        The Adoptions Team
        Saving Grace Animals for Adoption
        """

        html = """\
        <html>
          <body>
            <h2>An Update For Your Saving Grace Appointment</h2>
            <p>Hi """ + name + """,</p>
            <p>We wanted to follow up as we see the following notes you provided for your upcoming appointment:</p>
            <p><em>""" + appt.adopter_notes + """</em></p>
            <p>We are a little limited with dogs matching that description at this time.</p>
            <p>While your first choices may no longer be available, we do encourage you to keep your appointment. We always have wonderful dogs for you to visit with and always recommend keeping an open mind to see who may click with you. We also have dogs who have not had the chance to have photos taken and are not on our website yet.</p>
            <p>""" + reschedule_url + """</p>
            <p>""" + cancel_url + """</p>
            <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.</p>
            <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
          </body>
        </html>
        """

    send_email(text, html, "default", subject, email)

def ready_to_roll(appt, hw_status):
    subject = "An Update About Your Chosen Saving Grace Dog"
    adopter = appt.adopter_choice
    dog = appt.dog
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    date = appt.date
    today = datetime.datetime.today()

    #add in a factor for if already closed today (tomorrow only)

    if today.weekday() >= 4:
        next_business_day = 0
        next_bd_string = "Monday"
    else:
        next_business_day = today.weekday() + 1
        next_bd_string = "tomorrow"

    if next_business_day == 2:
        next_bd_opening_hour = next_bd_open(13, 0)
    else:
        next_bd_opening_hour = next_bd_open(12, 0)

    if hw_status == "negative":
        text = """\
        Hi """ + name + """,\n
        Good news! """ + dog + """ has completed their vetting, has tested negative for heartworms, and is ready to go home.\n
        We can complete the adoption anytime up to 5:30pm today. We are also open """ + next_bd_string + """ from """ + next_bd_opening_hour + """ to 5:30pm.\n
        It is in your dog's best interest to go home as soon as possible. If the adoption is not completed by the time we close """ + next_bd_string + """, we will release their hold and allow them to meet other potential forever families. Please respond to this email with a time that works for you to come on-site and complete the adoption.\n
        Please be sure to bring a valid form of identification for our records, as well as a means of paying our adoption fee. The fee can be paid by cash ($380, exact amount please unless you wish to make a donation) or credit/debit card ($380 plus $15 processing fee).\n
        Thank you so much for your patience. """ + dog + """ is wonderful and worth the wait!\n
        All the best, \n
        The Adoptions Team
        Saving Grace Animals for Adoption
        """

        html = """\
        <html>
          <body>
            <p>Hi """ + name + """,</p>
            <p>Good news! """ + dog + """ has completed their vetting, has tested negative for heartworms, and is ready to go home.</p>
            <p>We can complete the adoption anytime up to 5:30pm today. We are also open """ + next_bd_string + """ from """ + next_bd_opening_hour + """ to 5:30pm.</p>
            <p>It is in your dog's best interest to go home as soon as possible. If the adoption is not completed by the time we close """ + next_bd_string + """, we will release their hold and allow them to meet other potential forever families. Please respond to this email with a time that works for you to come on-site and complete the adoption.</p>
            <p>Please be sure to bring a valid form of identification for our records, as well as a means of paying our adoption fee. The fee can be paid by cash ($380, exact amount please unless you wish to make a donation) or credit/debit card ($380 plus $15 processing fee).</p>
            <p>Thank you so much for your patience. """ + dog + """ is wonderful and worth the wait!</p>
            <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
          </body>
        </html>
        """
    elif hw_status == "positive":
        text = """\
        Hi """ + name + """,\n
        Good news! """ + dog + """ has completed their vetting and is ready to go home.\n
        """ + dog + """ has also tested positive for heartworms, which is common in the Carolinas. This means he was bitten by an infected mosquito. Fortunately, heartworms are not contagious to other dogs or humans, and are treatable.\n
        """ + dog + """ will fall under our foster-to-adopt (FTA) program while undergoing heartworm treatments. This is a series of three injections administered over a four to six week period. We need to remain the legal owners of the dog in order to medically treat them, though it is highly important that you still establish baseline care with your personal veterinarian. You will be sent home with a copy of their medical records and will receive the originals upon final adoption (the day of the last injection). We can discuss this further with you when you come on-site to complete the FTA agreement.\n
        Once the series of injections is complete, you will only need to provide a monthly preventative. Your vet will retest in six to eight months to ensure the treatments were entirely successful.\n
        We can complete the FTA agreement anytime up to 5:30pm today. We are also open """ + next_bd_string + """ from """ + next_bd_opening_hour + """ to 5:30pm.\n
        It is in your dog's best interest to go home as soon as possible. If the adoption is not completed by the time we close """ + next_bd_string + """, we will release their hold and allow them to meet other potential forever families. Please respond to this email with a time that works for you to come on-site and complete the FTA agreement.\n
        Thank you so much for your patience. """ + dog + """ is wonderful and worth the wait!\n
        All the best, \n
        The Adoptions Team
        Saving Grace Animals for Adoption
        """

        html = """\
        <html>
          <body>
            <p>Hi """ + name + """,</p>
            <p>Good news! """ + dog + """ has completed their vetting and is ready to go home.</p>
            <p>""" + dog + """ has also tested positive for heartworms, which is common in the Carolinas. This means he was bitten by an infected mosquito. Fortunately, heartworms are not contagious to other dogs or humans, and are treatable.</p>
            <p>""" + dog + """ will fall under our foster-to-adopt (FTA) program while undergoing heartworm treatments. This is a series of three injections administered over a four to six week period. We need to remain the legal owners of the dog in order to medically treat them, though it is highly important that you still establish baseline care with your personal veterinarian. You will be sent home with a copy of their medical records and will receive the originals upon final adoption (the day of the last injection). We can discuss this further with you when you come on-site to complete the FTA agreement.</p>
            <p>Once the series of injections is complete, you will only need to provide a monthly preventative. Your vet will retest in six to eight months to ensure the treatments were entirely successful.</p>
            <p>We can complete the FTA agreement anytime up to 5:30pm today. We are also open """ + next_bd_string + """ from """ + next_bd_opening_hour + """ to 5:30pm.</p>
            <p>It is in your dog's best interest to go home as soon as possible. If the FTA agreement is not completed by the time we close """ + next_bd_string + """, we will release their hold and allow them to meet other potential forever families. Please respond to this email with a time that works for you to come on-site and complete the FTA agreement.</p>
            <p>Thank you so much for your patience. """ + dog + """ is wonderful and worth the wait!</p>
            <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
          </body>
        </html>
        """

    send_email(text, html, "default", subject, email)

def dogs_were_adopted(adopter, appt):
    subject = "An Update About Your Saving Grace Appointment"
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    date = appt.date

    plain_reschedule_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    reschedule_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">If you wish to reschedule your appointment, click here.</a>'

    plain_cancel_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    cancel_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">If you wish to cancel your appointment, click here.</a>'

    text = """\
    Hi """ + name + """,\n
    We wanted to follow up as we see the following notes you provided for your upcoming appointment:\n""" + appt.adopter_notes + """\n
    The dog(s) you mentioned above have found their forever homes.\n
    While your first choices may no longer be available, we do encourage you to keep your appointment. We always have wonderful dogs for you to visit with and always recommend keeping an open mind to see who may click with you. We also have dogs who have not had the chance to have photos taken and are not on our website yet.\n
    If you wish to reschedule your appointment, you can do so here: """ + plain_reschedule_url + """\n
    If you wish to cancel your appointment, you can do so here: """ + plain_cancel_url + """\n
    Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    """

    html = """\
    <html>
      <body>
        <h2>An Update For Your Saving Grace Appointment</h2>
        <p>Hi """ + name + """,</p>
        <p>We wanted to follow up as we see the following notes you provided for your upcoming appointment:</p>
        <p><em>""" + appt.adopter_notes + """</em></p>
        <p>The dog(s) you mentioned above have found their forever homes.</p>
        <p>While your first choices may no longer be available, we do encourage you to keep your appointment. We always have wonderful dogs for you to visit with and always recommend keeping an open mind to see who may click with you. We also have dogs who have not had the chance to have photos taken and are not on our website yet.</p>
        <p>""" + reschedule_url + """</p>
        <p>""" + cancel_url + """</p>
        <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def new_contact_adopter_msg(adopter, message, include_links):
    subject = "New message from the Saving Grace adoptions team"
    name = adopter.adopter_first_name
    email = adopter.adopter_email

    plain_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">Manage Your Appointment Here</a>'

    if include_links == True:
        text = """\
        Hi """ + name + """,\n
        """ + message + """\n
        Visit this website to manage your adoption appointment: """ + plain_url + """\n
        Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when scheduling, rescheduling, or cancelling an appointment.\n
        All the best, \n
        The Adoptions Team
        Saving Grace Animals for Adoption
        """

        html = """\
        <html>
          <body>
            <p>Hi """ + name + """,</p>
            <p>""" + message + """</p>
            <p>""" + url + """</p>
            <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
          </body>
        </html>
        """
    else:
        text = """\
        Hi """ + name + """,\n
        """ + message + """.\n
        All the best, \n
        The Adoptions Team
        Saving Grace Animals for Adoption
        """

        html = """\
        <html>
          <body>
            <p>Hi """ + name + """,</p>
            <p>""" + message + """</p>
            <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
          </body>
        </html>
        """

    send_email(text, html, "default", subject, email)

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
