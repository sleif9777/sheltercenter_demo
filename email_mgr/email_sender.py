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

    cancel_url = '<a href="http://{0}/calendar/adopter/cancel/adopter/{1}/appt/{2}/date/{3}/{4}/{5}/">Click here to cancel your appointment.</a>'.format(base_name, adopter.id, appt.id, appt.date.year, appt.date.month, appt.date.day)

    plain_cancel_url = 'http://{0}/calendar/adopter/cancel/adopter/{1}/appt/{2}/date/{3}/{4}/{5}/'.format(base_name, adopter.id, appt.id, appt.date.year, appt.date.month, appt.date.day)

    reschedule_url = '<a href="http://{0}/adopter/{1}/">Click here to reschedule your appointment.</a>'.format(base_name, adopter.id)

    plain_reschedule_url = 'http://{0}/adopter/{1}/'.format(base_name, adopter.id)

    html = html.replace(cancel_url, plain_cancel_url)
    html = html.replace(reschedule_url, plain_reschedule_url)

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

def simple_invite(fname, lname, email, subjnotes):
    subject = "Your adoption request has been reviewed: " + fname.upper() + " " + lname.upper()

    if subjnotes:
        subject += " (" + subjnotes + ")"

    text = """\
Congratulations, your Saving Grace adoption request has been reviewed and it is time to schedule your appointment. Please review the following information before responding. Many of our FAQs are addressed here.\n\n
Communicating with the Adoptions Team\n\n
- Our Adoptions Managers actively engage with dogs and onsite adopters during working hours. As a result, their response time to emails may be limited.\n
- Other team members who moderate this email are off-site and focus their volunteer efforts towards scheduling appointments and answering questions about our policies. They are not as familiar with the dogs. Please save all questions about specific dogs until you are on-site for your appointment - those you meet in-person will have the best answers for you.\n
- Our phone line is not monitored. We do not make phone calls to adopters.\n
- Multiple team members moderate this email. Please help us all stay on the same page by always responding directly to the last email you received from us.\n\n
Operating Hours\n\n
Monday: 12:00pm to 6:00pm\n
Tuesday: 12:00pm to 6:00pm\n
Wednesday: 1:00pm to 6:00pm (if interested in puppies, schedule for this day)\n
Thursday: 12:00pm to 6:00pm (if interested in puppies, schedule for this day)\n
Friday: 12:00pm to 6:00pm\n\n
We do not hold adoption appointments during mornings or weekends. There are no exceptions or flexibility offered in this regard.\n\n
Scheduling an Appointment\n\n
- Please respond with three specific dates and times that work for you. Giving us options helps us schedule you an appointment as fast as possible and saves everyone a lot of back-and-forth.\n
- Supply your own availability rather than ask ours. We are working with many adopters at once and our calendar can change from one moment to the next.\n
- Schedule for a day that you are fully prepared to take a dog home immediately following the appointment. We do not hold chosen dogs unless they need further veterinary care. If you have upcoming travel and are concerned that will disrupt your new pet's adjustment period, please plan your visit for after you return home.\n
- Bring your entire family, including children and dogs (no non-canine pets). It is very important not only for the entire family to be comfortable with the choice of dog, <b>but also for the dog to demonstrate that they are comfortable with the family as well.<b> We ask this in the interest of making a match that works for everyone. A video meeting is not a substitute, as dogs respond most strongly to scent and temperament, not appearance.\n
- Puppies arrive on Wednesdays and Thursdays and stay with us until they find a home. To have the best selection of puppies, please schedule for a Wednesday or Thursday. We cannot guarantee puppies to be available on Mondays, Tuesdays, or Fridays.\n
- Our puppies are of unknown parentage, we cannot guarantee them to grow to be any specific size.\n
- Appointments can be scheduled up to two weeks in advance. If you are looking to adopt later than two weeks in advance, please hold onto this email and respond closer to that time.\n
What To Expect During Your Appointment\n\n
- Your appointment is structured to take about one hour.\n
- You will have the opportunity to meet multiple available dogs.\n
- We strongly encourage adopters to keep an open mind and not narrow their scope to only one dog from the website. We likely have a good match for you, even if it isn't the dog you expect it to be. The more open you are to just engage in the process, the more potential options for dogs you will have.\n
- Dogs are not placed on hold. We do not accept deposits. It is important that you meet a dog in-person to experience their temperament and energy in-person. Our website's photos and short bios are only meant to be an introduction.\n
- If a dog is removed from the website, they have been adopted.\n
- It takes time for dogs to get photographed and posted to our website. There are always some available who haven't been posted and your match may be in that group. This is particularly true for small dogs, though we can let you know if we do not have many available.\n\n
Potential Adoption Outcomes\n\n
ADOPTABLE: Some of our dogs are ready to join their new families and will be able to leave the same day with you. If your dog falls into this category, you will need to take them home immediately following the appointment.\n\n
RESERVED/CHOSEN: Some of our dogs are newer to the program and may still require vetting before they can be adopted and go home. These are considered “Chosen” and will be unavailable for other adopters as they wait for what they need.\n\n
FOSTER TO ADOPT (FTA): We treat numerous dogs with heartworm disease, which is mosquito-borne and common throughout the Carolinas. If your chosen dog is heartworm-positive, he/she will be able to go home with you as a foster until the treatments are complete. We still need to legally own the dog in order to administer treatments, and so transfer of final adoption occurs after the third treatment. The process takes approximately 8-10 weeks. Adoptions Team members will discuss heartworm treatment with you and provide you further information during your appointment.\n\n
NO DECISION: It is possible you may not find your match during your appointment. You can schedule subsequent appointments until you do without filling out another application.\n\n

After having reviewed the above information, please respond directly to this email with upcoming availability and your desired size and age group in order to continue the adoption process. We look forward to working with you.\n\n

The Adoptions Team\n
Saving Grace Animals For Adoption
    """

    html = """\
    <html>
      <body>
        <p>Congratulations, your Saving Grace adoption request has been reviewed and it is time to schedule your appointment. Please review the following information before responding. Many of our FAQs are addressed here.</p>
        <h2 style="color: #C45389;">Communicating with the Adoptions Team</h2>
        <ul>
        <li>Our Adoptions Managers actively engage with dogs and onsite adopters during working hours. As a result, their response time to emails may be limited.</li>
        <li>Other team members who moderate this email are off-site and focus their volunteer efforts towards scheduling appointments and answering questions about our policies. They are not as familiar with the dogs. Please save all questions about specific dogs until you are on-site for your appointment - those you meet in-person will have the best answers for you.</li>
        <li>Our phone line is not monitored. We do not make phone calls to adopters.</li>
        <li>Multiple team members moderate this email. Please help us all stay on the same page by always responding directly to the last email you received from us.</li>
        </ul>
        <h2 style="color: #C45389;">Scheduling an Appointment</h2>
        <h3 style="color: #C45389;">Operating Hours</h3>
        <b>Monday: </b> 12:00pm to 6:00pm<br>
        <b>Tuesday: </b> 12:00pm to 6:00pm<br>
        <b>Wednesday: </b> 1:00pm to 6:00pm (if interested in puppies, schedule for this day)<br>
        <b>Thursday: </b> 12:00pm to 6:00pm (if interested in puppies, schedule for this day)<br>
        <b>Friday: </b> 12:00pm to 6:00pm<br>
        <ul>
        <li>We do not hold adoption appointments during mornings or weekends. There are no exceptions or flexibility offered in this regard.</li>
        </ul>
        <h3 style="color: #C45389;">Scheduling Policies</h3>
        <ul>
        <li>Respond with <b>three specific dates and times</b> that work for you. Giving us options helps us schedule you an appointment as fast as possible and saves everyone a lot of back-and-forth.</li>
        <li>Supply your own availability rather than ask ours. We are working with many adopters at once and our calendar can change from one moment to the next.</li>
        <li>Schedule for a day that you are fully prepared to take a dog home immediately following the appointment. We do not hold chosen dogs unless they need further veterinary care. If you have upcoming travel and are concerned that will disrupt your new pet's adjustment period, please plan your visit for after you return home.</li>
        <li>Bring your entire family, including children and dogs (no non-canine pets). It is very important not only for the entire family to be comfortable with the choice of dog, <b>but also for the dog to demonstrate that they are comfortable with the family as well.<b> We ask this in the interest of making a match that works for everyone. A video meeting is not a substitute, as dogs respond most strongly to scent and temperament, not appearance.</li>
        <li>Puppies arrive on Wednesdays and Thursdays and stay with us until they find a home. To have the best selection of puppies, please schedule for a Wednesday or Thursday. We cannot guarantee puppies to be available on Mondays, Tuesdays, or Fridays.</li>
        <li>Our puppies are of unknown parentage, we cannot guarantee them to grow to be any specific size.</li>
        <li>Appointments can be scheduled up to two weeks in advance. If you are looking to adopt later than two weeks in advance, please hold onto this email and respond closer to that time.</li>
        </ul>
        <h2 style="color: #C45389;">What To Expect During Your Appointment</h2>
        <li>Your appointment is structured to take about one hour.</li>
        <li>You will have the opportunity to meet multiple available dogs.</li>
        <li>We strongly encourage adopters to keep an open mind and not narrow their scope to only one dog from the website. We likely have a good match for you, even if it isn't the dog you expect it to be. The more open you are to just engage in the process, the more potential options for dogs you will have.</li>
        <li><b>Dogs are not placed on hold. We do not accept deposits.</b> It is important that you meet a dog in-person to experience their temperament and energy in-person. Our website's photos and short bios are only meant to be an introduction.</li>
        <li>If a dog is removed from the website, they have been adopted.</li>
        <li>It takes time for dogs to get photographed and posted to our website. There are always some available who haven't been posted and your match may be in that group. This is particularly true for small dogs, though we can let you know if we do not have many available.</li>
        <h3 style="color: #C45389;">Potential Adoption Outcomes</h3>
        <h4 style="color: #C45389;">Adoptable</h4>
        <p>Some of our dogs are ready to join their new families and will be able to leave the same day with you. If your dog falls into this category, you will need to take them home immediately following the appointment.</p>
        <h4 style="color: #C45389;">Reserved/Chosen</h4>
        <p>Some of our dogs are newer to the program and may still require vetting before they can be adopted and go home. These are considered “Chosen” and will be unavailable for other adopters as they wait for what they need.</p>
        <h4 style="color: #C45389;">Foster to Adopt (FTA)</h4>
        <p>We treat numerous dogs with heartworm disease, which is mosquito-borne and common throughout the Carolinas. If your chosen dog is heartworm-positive, he/she will be able to go home with you as a foster until the treatments are complete. We still need to legally own the dog in order to administer treatments, and so transfer of final adoption occurs after the third treatment. The process takes approximately 8-10 weeks. Adoptions Team members will discuss heartworm treatment with you and provide you further information during your appointment.</p>
        <h4 style="color: #C45389;">No Decision</h4>
        <p>It is possible you may not find your match during your appointment. You can schedule subsequent appointments until you do without filling out another application.</p>
        <p>After having reviewed the above information, please respond directly to this email with upcoming availability and your desired size and age group in order to continue the adoption process. We look forward to working with you.<p>
        <p>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "adoptions@savinggracenc.org", subject, email)


def simple_invite_oos(fname, lname, email, subjnotes):
    subject = "Your adoption request has been reviewed: " + fname.upper() + " " + lname.upper()

    if subjnotes:
        subject += " (" + subjnotes + ")"

    text = """\
Congratulations, your Saving Grace adoption request has been reviewed and it is time to schedule your appointment. Please review the following information before responding. Many of our FAQs are addressed here.\n\n
Out-Of-State Adoption Policies\n\n
We are happy to help adopters coming from a distance, but want to set appropriate expectations for adopting through our program.\n\n
- We do not ship or offer transport for adopted dogs. Each adopter must visit with an animal in person and commit to following through with adoption.\n
- In order to give the most dogs an opportunity for a forever family, dogs are not placed on hold. This means a dog you are considering may be adopted before your visit. It is best to visit with an open mind and choose a dog in person that best fits what you are looking for rather than be set on adopting a specific dog on the website.\n
- If a dog has not completed their veterinary care, an additional trip may be necessary at a later date to complete the adoption and pick up the dog. This process will vary with each animal and their medical needs. It is best to check with your veterinarian in your state of residence regarding health certificates/licensing required when bringing a new animal into your state. It is up to adopters to acquire the health certificate from a North Carolina veterinarian. While we can recommend veterinarians, we are unable to provide this service.\n\n
Communicating with the Adoptions Team\n\n
- Our Adoptions Managers actively engage with dogs and onsite adopters during working hours. As a result, their response time to emails may be limited.\n
- Other team members who moderate this email are off-site and focus their volunteer efforts towards scheduling appointments and answering questions about our policies. They are not as familiar with the dogs. Please save all questions about specific dogs until you are on-site for your appointment - those you meet in-person will have the best answers for you.\n
- Our phone line is not monitored. We do not make phone calls to adopters.\n
- Multiple team members moderate this email. Please help us all stay on the same page by always responding directly to the last email you received from us.\n\n
Operating Hours\n\n
Monday: 12:00pm to 6:00pm\n
Tuesday: 12:00pm to 6:00pm\n
Wednesday: 1:00pm to 6:00pm (if interested in puppies, schedule for this day)\n
Thursday: 12:00pm to 6:00pm (if interested in puppies, schedule for this day)\n
Friday: 12:00pm to 6:00pm\n\n
We do not hold adoption appointments during mornings or weekends. There are no exceptions or flexibility offered in this regard.\n\n
Scheduling an Appointment\n\n
- Please respond with three specific dates and times that work for you. Giving us options helps us schedule you an appointment as fast as possible and saves everyone a lot of back-and-forth.\n
- Please supply your own availability rather than ask ours. We are working with many adopters at once and our calendar can change from one moment to the next.\n
- We ask that you schedule for a day that you are fully prepared to take a dog home immediately following the appointment. We do not hold chosen dogs unless they need further veterinary care. If you have upcoming travel and are concerned that will disrupt your new pet's adjustment period, please schedule an appointment for after you return home.\n
- Please bring your entire family, including children and dogs (no non-canine pets). It is very important not only for the entire family to be comfortable with the choice of dog, <b>but also for the dog to demonstrate that they are comfortable with the family as well.<b> We ask this in the interest of making a match that works for everyone. A video meeting is not a substitute, as dogs respond most strongly to scent and temperament, not appearance.\n
- Puppies arrive on Wednesdays and Thursdays and stay with us until they find a home. To have the best selection of puppies, please schedule for a Wednesday or Thursday. We cannot guarantee puppies to be available on Mondays, Tuesdays, or Fridays.\n
- Our puppies are of unknown parentage, we cannot guarantee them to grow to be any specific size.\n
- Appointments can be scheduled up to two weeks in advance. If you are looking to adopt later than two weeks in advance, please hold onto this email and respond closer to that time.\n
What To Expect During Your Appointment\n\n
- Your appointment is structured to take about one hour.\n
- You will have the opportunity to meet multiple available dogs.\n
- We strongly encourage adopters to keep an open mind and not narrow their scope to only one dog from the website. We likely have a good match for you, even if it isn't the dog you expect it to be. The more open you are to just engage in the process, the more potential options for dogs you will have.\n
- Dogs are not placed on hold. We do not accept deposits. It is important that you meet a dog in-person to experience their temperament and energy in-person. Our website's photos and short bios are only meant to be an introduction.\n
- If a dog is removed from the website, they have been adopted.\n
- It takes time for dogs to get photographed and posted to our website. There are always some available who haven't been posted and your match may be in that group. This is particularly true for small dogs, though we can let you know if we do not have many available.\n\n
Potential Adoption Outcomes\n\n
ADOPTABLE: Some of our dogs are ready to join their new families and will be able to leave the same day with you. If your dog falls into this category, you will need to take them home immediately following the appointment.\n\n
RESERVED/CHOSEN: Some of our dogs are newer to the program and may still require vetting before they can be adopted and go home. These are considered “Chosen” and will be unavailable for other adopters as they wait for what they need.\n\n
FOSTER TO ADOPT (FTA): We treat numerous dogs with heartworm disease, which is mosquito-borne and common throughout the Carolinas. If your chosen dog is heartworm-positive, he/she will be able to go home with you as a foster until the treatments are complete. We still need to legally own the dog in order to administer treatments, and so transfer of final adoption occurs after the third treatment. The process takes approximately 8-10 weeks. Adoptions Team members will discuss heartworm treatment with you and provide you further information during your appointment.\n\n
NO DECISION: It is possible you may not find your match during your appointment. You can schedule subsequent appointments until you do without filling out another application.\n\n

After having reviewed the above information, please respond directly to this email with upcoming availability and your desired size and age group in order to continue the adoption process. We look forward to working with you.\n\n

The Adoptions Team\n
Saving Grace Animals For Adoption
    """

    html = """\
    <html>
      <body>
        <p>Congratulations, your Saving Grace adoption request has been reviewed and it is time to schedule your appointment. Please review the following information before responding. Many of our FAQs are addressed here.</p>
        <h2 style="color: #C45389;">Out-Of-State Adoption Policies</h2>
        <p>We are happy to help adopters coming from a distance, but want to set appropriate expectations for adopting through our program.</p>
        <ul>
        <li>We do not ship or offer transport for adopted dogs. Each adopter must visit with an animal in person and commit to following through with adoption.</li>
        <li>In order to give the most dogs an opportunity for a forever family, <b>dogs are not placed on hold.</b> This means a dog you are considering may be adopted before your visit. It is best to visit with an open mind and choose a dog in person that best fits what you are looking for rather than be set on adopting a specific dog on the website.</li>
        <li>If a dog has not completed their veterinary care, an additional trip may be necessary at a later date to complete the adoption and pick up the dog. This process will vary with each animal and their medical needs. It is best to check with your veterinarian in your state of residence regarding health certificates/licensing required when bringing a new animal into your state. It is up to adopters to acquire the health certificate from a North Carolina veterinarian. While we can recommend veterinarians, we are unable to provide this service.</li>
        </ul>
        <h2 style="color: #C45389;">Communicating with the Adoptions Team</h2>
        <ul>
        <li>Our Adoptions Managers actively engage with dogs and onsite adopters during working hours. As a result, their response time to emails may be limited.</li>
        <li>Other team members who moderate this email are off-site and focus their volunteer efforts towards scheduling appointments and answering questions about our policies. They are not as familiar with the dogs. Please save all questions about specific dogs until you are on-site for your appointment - those you meet in-person will have the best answers for you.</li>
        <li>Our phone line is not monitored. We do not make phone calls to adopters.</li>
        <li>Multiple team members moderate this email. Please help us all stay on the same page by always responding directly to the last email you received from us.</li>
        </ul>
        <h2 style="color: #C45389;">Scheduling an Appointment</h2>
        <h3 style="color: #C45389;">Operating Hours</h3>
        <b>Monday: </b> 12:00pm to 6:00pm<br>
        <b>Tuesday: </b> 12:00pm to 6:00pm<br>
        <b>Wednesday: </b> 1:00pm to 6:00pm (if interested in puppies, schedule for this day)<br>
        <b>Thursday: </b> 12:00pm to 6:00pm (if interested in puppies, schedule for this day)<br>
        <b>Friday: </b> 12:00pm to 6:00pm<br>
        <ul>
        <li>We do not hold adoption appointments during mornings or weekends. There are no exceptions or flexibility offered in this regard.</li>
        </ul>
        <h3 style="color: #C45389;">Scheduling Policies</h3>
        <ul>
        <li>Please respond with <b>three specific dates and times</b> that work for you. Giving us options helps us schedule you an appointment as fast as possible and saves everyone a lot of back-and-forth.</li>
        <li>Please supply your own availability rather than ask ours. We are working with many adopters at once and our calendar can change from one moment to the next.</li>
        <li>We ask that you schedule for a day that you are fully prepared to take a dog home immediately following the appointment. We do not hold chosen dogs unless they need further veterinary care. If you have upcoming travel and are concerned that will disrupt your new pet's adjustment period, please schedule an appointment for after you return home.</li>
        <li>Please bring your entire family, including children and dogs (no non-canine pets). It is very important not only for the entire family to be comfortable with the choice of dog, <b>but also for the dog to demonstrate that they are comfortable with the family as well.<b> We ask this in the interest of making a match that works for everyone. A video meeting is not a substitute, as dogs respond most strongly to scent and temperament, not appearance.</li>
        <li>Puppies arrive on Wednesdays and Thursdays and stay with us until they find a home. To have the best selection of puppies, please schedule for a Wednesday or Thursday. We cannot guarantee puppies to be available on Mondays, Tuesdays, or Fridays.</li>
        <li>Our puppies are of unknown parentage, we cannot guarantee them to grow to be any specific size.</li>
        <li>Appointments can be scheduled up to two weeks in advance. If you are looking to adopt later than two weeks in advance, please hold onto this email and respond closer to that time.</li>
        </ul>
        <h2 style="color: #C45389;">What To Expect During Your Appointment</h2>
        <li>Your appointment is structured to take about one hour.</li>
        <li>You will have the opportunity to meet multiple available dogs.</li>
        <li>We strongly encourage adopters to keep an open mind and not narrow their scope to only one dog from the website. We likely have a good match for you, even if it isn't the dog you expect it to be. The more open you are to just engage in the process, the more potential options for dogs you will have.</li>
        <li><b>Dogs are not placed on hold. We do not accept deposits.</b> It is important that you meet a dog in-person to experience their temperament and energy in-person. Our website's photos and short bios are only meant to be an introduction.</li>
        <li>If a dog is removed from the website, they have been adopted.</li>
        <li>It takes time for dogs to get photographed and posted to our website. There are always some available who haven't been posted and your match may be in that group. This is particularly true for small dogs, though we can let you know if we do not have many available.</li>
        <h3 style="color: #C45389;">Potential Adoption Outcomes</h3>
        <h4 style="color: #C45389;">Adoptable</h4>
        <p>Some of our dogs are ready to join their new families and will be able to leave the same day with you. If your dog falls into this category, you will need to take them home immediately following the appointment.</p>
        <h4 style="color: #C45389;">Reserved/Chosen</h4>
        <p>Some of our dogs are newer to the program and may still require vetting before they can be adopted and go home. These are considered “Chosen” and will be unavailable for other adopters as they wait for what they need.</p>
        <h4 style="color: #C45389;">Foster to Adopt (FTA)</h4>
        <p>We treat numerous dogs with heartworm disease, which is mosquito-borne and common throughout the Carolinas. If your chosen dog is heartworm-positive, he/she will be able to go home with you as a foster until the treatments are complete. We still need to legally own the dog in order to administer treatments, and so transfer of final adoption occurs after the third treatment. The process takes approximately 8-10 weeks. Adoptions Team members will discuss heartworm treatment with you and provide you further information during your appointment.</p>
        <h4 style="color: #C45389;">No Decision</h4>
        <p>It is possible you may not find your match during your appointment. You can schedule subsequent appointments until you do without filling out another application.</p>
        <p>After having reviewed the above information, please respond directly to this email with upcoming availability and your desired size and age group in order to continue the adoption process. We look forward to working with you.<p>
        <p>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "adoptions@savinggracenc.org", subject, email)

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
        print("yes2!")
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
        print(html)
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

    print(today.weekday())
    print(type(today.weekday()))

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

    print(html)
    print(text)

    send_email(text, html, "default", subject, email)

def reschedule(time, date, adopter, appt):
    subject = "Your appointment has been rescheduled: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    plain_reschedule_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    reschedule_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">Click here to reschedule your appointment.</a>'

    plain_cancel_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    cancel_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Click here to cancel your appointment.</a>'

    time, date = clean_time_and_date(time, date)

    text = """\
    Appointment Rescheduled\n
    Hi """ + name + """,\n
    Your appointment has been rescheduled for """ + time + """ on """ + date + """.\n
    You can reschedule your appointment here: """ + plain_reschedule_url + """\n
    You can cancel your appointment here: """ + plain_cancel_url + """\n
    Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.\n
    We have included the Visitor Instructions from your original confirmation email for your reference.\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    \n\n
    Visitor Instructions\n\n
    Directions:\n
    Our address is 13400 Old Creedmoor Rd, Wake Forest, NC, located behind Harris Teeter at the intersection of NC-98 and Old Creedmoor Rd. We are just under a mile west of the NC-98 and NC-50 intersection. You will see a teal shed with butterflies at the end of our driveway. Once parked, enter through the gate located in the far back left corner of the parking lot and check in with the greeter. Please do not pull into the driveway with the closed wooden gate or use the neighbor’s driveway to turn around. We request you go down to the next street to make your U-turn. We appreciate your help in respecting our neighbor's privacy and property.\n\n
    Dress for the Occasion:\n
    Be prepared to meet a friendly furry welcoming committee! Everyone is well behaved, but they get very excited and may jump on you. All our meeting areas are outside, so dress for comfort according to the weather. We continue with appointments even if it is raining, so dress appropriately.\n\n
    Hydration:\n
    It can be quite hot on the farm, so please make sure to bring water with you. We want you to enjoy your time while meeting dogs and staying hydrated will help with that.</p>
    Restrooms:\n
    We have a port-a-potty available for use at the farm. There are also public facilities available at Harris Teeter.\n\n
    Supplies:\n
    When you adopt one of our dogs, they will go home with a collar and a slip leash. Most new owners find it best to take their new dog shopping with them to find the appropriately sized items. Our Saving Grace Supply Co. store, located at the intersection of NC-98 and Six Forks Rd (about two miles east of our farm), carries many essential supplies.\n\n
    Adoption Fee:\n
    We accept credit/debit card or cash. We do not accept personal checks. Our adoption fee is $380.00. There is an additional $15 credit/debit card fee. If using cash, please bring the exact amount as we do not keep change onsite. Otherwise, we would be happy to accept the extra as a donation. This fee covers the medical costs and expenses which ensure that your dog comes to you altered, microchipped, up to date on all vaccinations, on preventatives for fleas, ticks, and heartworms, and having received a baseline wellness exam.\n\n
    Training:\n
    Many of our dogs have crate experience, but please have realistic expectations. We cannot guarantee any dog to be entirely housetrained. A transition period is to be expected for any new dog as they get used to your home. Remember your lifestyle and routine will be new to your dog and it will be your responsibility to acclimate them to your home.\n\n
    Bringing Your Dog:\n
    You are welcome to bring your dog, but we do want to let you know that we do not have any off leash meet and greet areas and so all meetings take place on leash in the parking lot. In the warmer seasons, your dog will need to wait in the parking lot with a family member. If it is cool enough, they may wait in the car while you meet potential buddies.\n\n
    Canceling and Rescheduling:\n
    If you can no longer make your scheduled appointment, please give us the courtesy of 24 hours’ notice (or as soon as possible, if scheduled within 24 hours) so we may offer the slot to another adopter. If you wish to reschedule within two weeks, please provide at least three specific alternate dates and times so that we have options to work with. As a reminder, our hours are noon to 6pm on Mondays/Tuesdays/Thursdays/Fridays and 1pm to 6pm on Wednesdays. We do not offer morning or weekend appointments and there is no flexibility in this regard.\n\n
    A Special Note for Renters:\n
    We will assume you have standard breed restrictions unless you provide a written statement from your landlord or property manager that indicates otherwise. As the adopter, you should always do your own due diligence in communicating directly with your landlord or property manager and verifying if they have restrictions (size, weight, age, breeds, maximum number of pets, etc.) before your visit as the lease is between you and them.
    """

    html = """\
    <html>
      <body>
        <h2>Appointment Confirmation</h2>
        <p>Hi """ + name + """,</p>
        <p>Your appointment has been rescheduled for """ + time + """ on """ + date + """.</p>
        <p>""" + reschedule_url + """</p>
        <p>""" + cancel_url + """</p>
        <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.</p>
        <p>We have included the Visitor Instructions from your original confirmation email for your reference.</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
        <h2>Visitor Instructions</h2>
        <h3>Directions</h3>
        <p>Our address is 13400 Old Creedmoor Rd, Wake Forest, NC, located behind Harris Teeter at the intersection of NC-98 and Old Creedmoor Rd. We are just under a mile west of the NC-98 and NC-50 intersection. You will see a teal shed with butterflies at the end of our driveway. Once parked, enter through the gate located in the far back left corner of the parking lot and check in with the greeter. Please do not pull into the driveway with the closed wooden gate or use the neighbor’s driveway to turn around. We request you go down to the next street to make your U-turn. We appreciate your help in respecting our neighbor's privacy and property.</p>
        <h3>Dress for the Occasion</h3>
        <p>Be prepared to meet a friendly furry welcoming committee! Everyone is well behaved, but they get very excited and may jump on you. All our meeting areas are outside, so dress for comfort according to the weather. We continue with appointments even if it is raining, so dress appropriately.</p>
        <h3>Hydration</h3>
        <p>It can be quite hot on the farm, so please make sure to bring water with you. We want you to enjoy your time while meeting dogs and staying hydrated will help with that.</p>
        <h3>Restrooms</h3>
        <p>We have a port-a-potty available for use at the farm. There are also public facilities available at Harris Teeter.</p>
        <h3>Supplies</h3>
        <p>When you adopt one of our dogs, they will go home with a collar and a slip leash. Most new owners find it best to take their new dog shopping with them to find the appropriately sized items. Our Saving Grace Supply Co. store, located at the intersection of NC-98 and Six Forks Rd (about two miles east of our farm), carries many essential supplies.</p>
        <h3>Adoption Fee</h3>
        <p>We accept credit/debit card or cash. We do not accept personal checks. Our adoption fee is $380.00. There is an additional $15 credit/debit card fee. If using cash, please bring the exact amount as we do not keep change onsite. Otherwise, we would be happy to accept the extra as a donation. This fee covers the medical costs and expenses which ensure that your dog comes to you altered, microchipped, up to date on all vaccinations, on preventatives for fleas, ticks, and heartworms, and having received a baseline wellness exam.</p>
        <h3>Training</h3>
        <p>Many of our dogs have crate experience, but please have realistic expectations. We cannot guarantee any dog to be entirely housetrained. A transition period is to be expected for any new dog as they get used to your home. Remember your lifestyle and routine will be new to your dog and it will be your responsibility to acclimate them to your home.</p>
        <h3>Bringing Your Dog</h3>
        <p>You are welcome to bring your dog, but we do want to let you know that we do not have any off leash meet and greet areas and so all meetings take place on leash in the parking lot. In the warmer seasons, your dog will need to wait in the parking lot with a family member. If it is cool enough, they may wait in the car while you meet potential buddies.</p>
        <h3>Canceling and Rescheduling</h3>
        <p>If you can no longer make your scheduled appointment, please give us the courtesy of 24 hours’ notice (or as soon as possible, if scheduled within 24 hours) so we may offer the slot to another adopter. If you wish to reschedule within two weeks, please provide at least three specific alternate dates and times so that we have options to work with. As a reminder, our hours are noon to 6pm on Mondays/Tuesdays/Thursdays/Fridays and 1pm to 6pm on Wednesdays. We do not offer morning or weekend appointments and there is no flexibility in this regard.</p>
        <h3>A Special Note for Renters</h3>
        <p>We will assume you have standard breed restrictions unless you provide a written statement from your landlord or property manager that indicates otherwise. As the adopter, you should always do your own due diligence in communicating directly with your landlord or property manager and verifying if they have restrictions (size, weight, age, breeds, maximum number of pets, etc.) before your visit as the lease is between you and them.</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def greeter_reschedule_email(time, date, adopter, appt):
    subject = "Your follow-up appointment has been scheduled: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    plain_reschedule_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    reschedule_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">Click here to reschedule your appointment.</a>'

    plain_cancel_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    cancel_url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/calendar/adopter/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Click here to cancel your appointment.</a>'

    time, date = clean_time_and_date(time, date)

    text = """\
    Appointment Rescheduled\n
    Hi """ + name + """,\n
    Your follow-up appointment has been scheduled for """ + time + """ on """ + date + """.\n
    You can reschedule your appointment here: """ + plain_reschedule_url + """\n
    You can cancel your appointment here: """ + plain_cancel_url + """\n
    Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.\n
    We have included the Visitor Instructions from your original confirmation email for your reference.\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    \n\n
    Visitor Instructions\n\n
    Directions:\n
    Our address is 13400 Old Creedmoor Rd, Wake Forest, NC, located behind Harris Teeter at the intersection of NC-98 and Old Creedmoor Rd. We are just under a mile west of the NC-98 and NC-50 intersection. You will see a teal shed with butterflies at the end of our driveway. Once parked, enter through the gate located in the far back left corner of the parking lot and check in with the greeter. Please do not pull into the driveway with the closed wooden gate or use the neighbor’s driveway to turn around. We request you go down to the next street to make your U-turn. We appreciate your help in respecting our neighbor's privacy and property.\n\n
    Dress for the Occasion:\n
    Be prepared to meet a friendly furry welcoming committee! Everyone is well behaved, but they get very excited and may jump on you. All our meeting areas are outside, so dress for comfort according to the weather. We continue with appointments even if it is raining, so dress appropriately.\n\n
    Hydration:\n
    It can be quite hot on the farm, so please make sure to bring water with you. We want you to enjoy your time while meeting dogs and staying hydrated will help with that.</p>
    Restrooms:\n
    We have a port-a-potty available for use at the farm. There are also public facilities available at Harris Teeter.\n\n
    Supplies:\n
    When you adopt one of our dogs, they will go home with a collar and a slip leash. Most new owners find it best to take their new dog shopping with them to find the appropriately sized items. Our Saving Grace Supply Co. store, located at the intersection of NC-98 and Six Forks Rd (about two miles east of our farm), carries many essential supplies.\n\n
    Adoption Fee:\n
    We accept credit/debit card or cash. We do not accept personal checks. Our adoption fee is $380.00. There is an additional $15 credit/debit card fee. If using cash, please bring the exact amount as we do not keep change onsite. Otherwise, we would be happy to accept the extra as a donation. This fee covers the medical costs and expenses which ensure that your dog comes to you altered, microchipped, up to date on all vaccinations, on preventatives for fleas, ticks, and heartworms, and having received a baseline wellness exam.\n\n
    Training:\n
    Many of our dogs have crate experience, but please have realistic expectations. We cannot guarantee any dog to be entirely housetrained. A transition period is to be expected for any new dog as they get used to your home. Remember your lifestyle and routine will be new to your dog and it will be your responsibility to acclimate them to your home.\n\n
    Bringing Your Dog:\n
    You are welcome to bring your dog, but we do want to let you know that we do not have any off leash meet and greet areas and so all meetings take place on leash in the parking lot. In the warmer seasons, your dog will need to wait in the parking lot with a family member. If it is cool enough, they may wait in the car while you meet potential buddies.\n\n
    Canceling and Rescheduling:\n
    If you can no longer make your scheduled appointment, please give us the courtesy of 24 hours’ notice (or as soon as possible, if scheduled within 24 hours) so we may offer the slot to another adopter. If you wish to reschedule within two weeks, please provide at least three specific alternate dates and times so that we have options to work with. As a reminder, our hours are noon to 6pm on Mondays/Tuesdays/Thursdays/Fridays and 1pm to 6pm on Wednesdays. We do not offer morning or weekend appointments and there is no flexibility in this regard.\n\n
    A Special Note for Renters:\n
    We will assume you have standard breed restrictions unless you provide a written statement from your landlord or property manager that indicates otherwise. As the adopter, you should always do your own due diligence in communicating directly with your landlord or property manager and verifying if they have restrictions (size, weight, age, breeds, maximum number of pets, etc.) before your visit as the lease is between you and them.
    """

    html = """\
    <html>
      <body>
        <h2>Appointment Confirmation</h2>
        <p>Hi """ + name + """,</p>
        <p>Your appointment has been rescheduled for """ + time + """ on """ + date + """.</p>
        <p>""" + reschedule_url + """</p>
        <p>""" + cancel_url + """</p>
        <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this if you cancel or reschedule your appointment.</p>
        <p>We have included the Visitor Instructions from your original confirmation email for your reference.</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
        <h2>Visitor Instructions</h2>
        <h3>Directions</h3>
        <p>Our address is 13400 Old Creedmoor Rd, Wake Forest, NC, located behind Harris Teeter at the intersection of NC-98 and Old Creedmoor Rd. We are just under a mile west of the NC-98 and NC-50 intersection. You will see a teal shed with butterflies at the end of our driveway. Once parked, enter through the gate located in the far back left corner of the parking lot and check in with the greeter. Please do not pull into the driveway with the closed wooden gate or use the neighbor’s driveway to turn around. We request you go down to the next street to make your U-turn. We appreciate your help in respecting our neighbor's privacy and property.</p>
        <h3>Dress for the Occasion</h3>
        <p>Be prepared to meet a friendly furry welcoming committee! Everyone is well behaved, but they get very excited and may jump on you. All our meeting areas are outside, so dress for comfort according to the weather. We continue with appointments even if it is raining, so dress appropriately.</p>
        <h3>Hydration</h3>
        <p>It can be quite hot on the farm, so please make sure to bring water with you. We want you to enjoy your time while meeting dogs and staying hydrated will help with that.</p>
        <h3>Restrooms</h3>
        <p>We have a port-a-potty available for use at the farm. There are also public facilities available at Harris Teeter.</p>
        <h3>Supplies</h3>
        <p>When you adopt one of our dogs, they will go home with a collar and a slip leash. Most new owners find it best to take their new dog shopping with them to find the appropriately sized items. Our Saving Grace Supply Co. store, located at the intersection of NC-98 and Six Forks Rd (about two miles east of our farm), carries many essential supplies.</p>
        <h3>Adoption Fee</h3>
        <p>We accept credit/debit card or cash. We do not accept personal checks. Our adoption fee is $380.00. There is an additional $15 credit/debit card fee. If using cash, please bring the exact amount as we do not keep change onsite. Otherwise, we would be happy to accept the extra as a donation. This fee covers the medical costs and expenses which ensure that your dog comes to you altered, microchipped, up to date on all vaccinations, on preventatives for fleas, ticks, and heartworms, and having received a baseline wellness exam.</p>
        <h3>Training</h3>
        <p>Many of our dogs have crate experience, but please have realistic expectations. We cannot guarantee any dog to be entirely housetrained. A transition period is to be expected for any new dog as they get used to your home. Remember your lifestyle and routine will be new to your dog and it will be your responsibility to acclimate them to your home.</p>
        <h3>Bringing Your Dog</h3>
        <p>You are welcome to bring your dog, but we do want to let you know that we do not have any off leash meet and greet areas and so all meetings take place on leash in the parking lot. In the warmer seasons, your dog will need to wait in the parking lot with a family member. If it is cool enough, they may wait in the car while you meet potential buddies.</p>
        <h3>Canceling and Rescheduling</h3>
        <p>If you can no longer make your scheduled appointment, please give us the courtesy of 24 hours’ notice (or as soon as possible, if scheduled within 24 hours) so we may offer the slot to another adopter. If you wish to reschedule within two weeks, please provide at least three specific alternate dates and times so that we have options to work with. As a reminder, our hours are noon to 6pm on Mondays/Tuesdays/Thursdays/Fridays and 1pm to 6pm on Wednesdays. We do not offer morning or weekend appointments and there is no flexibility in this regard.</p>
        <h3>A Special Note for Renters</h3>
        <p>We will assume you have standard breed restrictions unless you provide a written statement from your landlord or property manager that indicates otherwise. As the adopter, you should always do your own due diligence in communicating directly with your landlord or property manager and verifying if they have restrictions (size, weight, age, breeds, maximum number of pets, etc.) before your visit as the lease is between you and them.</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def duplicate_app(adopter):
    subject = "We already have you in our database: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    plain_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">You can schedule an appointment at any time by clicking here.</a>'

    text = """\
    Hi """ + name + """,\n
    Thank you for sending in your most recent application.\n
    We already have you in our database. Your application is not specific to any one dog and we do not require a new one for each visit. If you would like to schedule an appointment, visit this website:\n""" + plain_url + """\n
    Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.\n
    If you are having trouble using this website, please reply to this email so we can best help you.\n
    All the best, \n
    The Adoptions Team\n
    Saving Grace Animals for Adoption
    """

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>Thank you for sending in your most recent application.</p>
        <p>We already have you in our database. Your application is not specific to any one dog and we do not require a new one for each visit. """ + url + """</p>
        <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.</p>
        <p>If you are having trouble using this website, please reply to this email so we can best help you.</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def follow_up(adopter):
    subject = "Thank you for visiting: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    plain_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">If you would like to schedule another appointment, click here.</a>'

    text = """\
    Hi """ + name + """,\n
    Thank you for visiting the Funny Farm today!\n
    We are sorry we were not able to match you with anyone today. There are always great dogs entering our program, and your new best friend may be here soon! If you would like to schedule another appointment, visit this website:\n""" + plain_url + """\n
    Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.\n
    We hope to welcome you back soon.\n
    All the best, \n
    The Adoptions Team\n
    Saving Grace Animals for Adoption
    """

    html = """\
    <html>
      <body>
        <h2>Thank you for visiting!</h2>
        <p>Hi """ + name + """,</p>
        <p>Thank you for visiting the Funny Farm today!</p>
        <p>We are sorry we were not able to match you with anyone today. There are always great dogs entering our program, and your new best friend may be here soon! """ + url + """</p>
        <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.</p>
        <p>We hope to welcome you back soon.</p
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def follow_up_w_host(adopter):
    subject = "Thank you for visiting: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    plain_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">If you would like to schedule another appointment, click here.</a>'

    plain_host_url = 'https://savinggracenc.org/host-a-dog/'
    host_url = '<a href="https://savinggracenc.org/host-a-dog/">If you would like to learn more about our Weekend Host program, click here.</a>'

    text = """\
    Hi """ + name + """,\n
    Thank you for visiting the Funny Farm today!\n
    We are sorry we were not able to match you with anyone today. There are always great dogs entering our program, and your new best friend may be here soon! If you would like to schedule another appointment, visit this website:\n""" + plain_url + """\n
    Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.\n
    We also mentioned the possibility of participating in our Weekend Host program. This program runs every weekend (when we do not hold appointments) to give our long-time residents a break from the noisy and busy shelter environment. You would provide us some baseline information on your household (i.e. other pets, children in home, fenced yard, desired size) and be matched with an available dog who would fit well with your home. You would not get to pick your host dog yourself, but you would get first priority to adopt them if the match proves to be a good fit. For more information on Weekend Host, visit this website: """ + plain_host_url + """\n
    We hope to welcome you back soon.\n
    All the best, \n
    The Adoptions Team\n
    Saving Grace Animals for Adoption
    """

    html = """\
    <html>
      <body>
        <h2>Thank you for visiting!</h2>
        <p>Hi """ + name + """,</p>
        <p>Thank you for visiting the Funny Farm today!</p>
        <p>We are sorry we were not able to match you with anyone today. There are always great dogs entering our program, and your new best friend may be here soon! """ + url + """</p>
        <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.</p>
        <p>We also mentioned the possibility of participating in our Weekend Host program. This program runs every weekend (when we do not hold appointments) to give our long-time residents a break from the noisy and busy shelter environment. You would provide us some baseline information on your household (i.e. other pets, children in home, fenced yard, desired size) and be matched with an available dog who would fit well with your home. You would not get to pick your host dog yourself, but you would get first priority to adopt them if the match proves to be a good fit. """ + host_url + """</p>
        <p>We hope to welcome you back soon.</p
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def invite(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    plain_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">You may review our response by clicking here.</a>'

    text = """\
Hi """ + name + """,\n
Your Saving Grace adoption request has been reviewed. You may review our response here:\n""" + plain_url + """\n
Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.\n
If you are a current foster or host who is adopting your foster/host dog, please respond directly to this email so we can proceed accordingly.\n
If you are having technical issues with our scheduling software, please email us directly so we can best help.\n
Thank you,
The Adoptions Team\n
Saving Grace Animals for Adoption
"""

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>Your Saving Grace adoption request has been reviewed. """ + url + """</p>
        <p>Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.</p>
        <p>If you are a current foster or host who is adopting your foster/host dog, please respond directly to this email so we can proceed accordingly.</p>
        <p>If you are having technical issues with our scheduling software, please email us directly so we can best help.</p>
        <p>Thank you,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def invite_oos(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    plain_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">After reading these special expectations for long-distance adoption, you may click here to continue forward in our process, review our standard adoption expectations, and schedule an appointment.</a>'

    text = """\
Hi """ + name + """,\n
Thank you for considering adoption through Saving Grace in North Carolina where we always have great dogs waiting for homes.\n
We are happy to help out of state adopters and want to provide appropriate expectations for long-distance adoption. We do not ship or offer transport for adopted dogs. Each adopter must visit with an animal in person and commit to following through with adoption. In order to give the most dogs an opportunity for a forever family, dogs are not placed on hold. This means a dog you are considering may be adopted before your visit. It is best to visit with an open mind and choose a dog in person that best fits what you are looking for rather than be set on adopting a specific dog on the website.\n
If a dog has not completed their veterinary care, an additional trip may be necessary at a later date to complete the adoption and pick up the dog. This process will vary with each animal and their medical needs. It is best to check with your veterinarian in your state of residence regarding health certificates/licensing required when bringing a new animal into your state. It is up to adopters to acquire the health certificate from a North Carolina veterinarian. While we can recommend veterinarians, we are unable to provide this service.\n
After reading these special expectations for long-distance adoption, you may continue to review our standard adoption expectations and schedule an appointment here: \n""" + plain_url + """\n
Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.\n
Thank you,
The Adoptions Team\n
Saving Grace Animals for Adoption
"""

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>Thank you for considering adoption through Saving Grace in North Carolina where we always have great dogs waiting for homes.</p>
        <p>We are happy to help out of state adopters and want to provide appropriate expectations for long-distance adoption. We do not ship or offer transport for adopted dogs. Each adopter must visit with an animal in person and commit to following through with adoption. In order to give the most dogs an opportunity for a forever family, dogs are not placed on hold. This means a dog you are considering may be adopted before your visit. It is best to visit with an open mind and choose a dog in person that best fits what you are looking for rather than be set on adopting a specific dog on the website.</p>
        <p>If a dog has not completed their veterinary care, an additional trip may be necessary at a later date to complete the adoption and pick up the dog. This process will vary with each animal and their medical needs. It is best to check with your veterinarian in your state of residence regarding health certificates/licensing required when bringing a new animal into your state. It is up to adopters to acquire the health certificate from a North Carolina veterinarian. While we can recommend veterinarians, we are unable to provide this service.</p>
        <p>""" + url + """</p>
        <p>Thank you,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def invite_lives_w_parents(adopter):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    plain_url = 'http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://sheltercenter-v2l7h.ondigitalocean.app/adopter/' + str(adopter.id) + '/">You may review our adoption policies and schedule an appointment by clicking here.</a>'

    text = """\
Hi """ + name + """,\n
Your Saving Grace adoption request has been reviewed and approved.\n
We did notice on your application that you live with your family. It is our policy to require at least one parent attend any appointment with you. While the choice of dog is ultimately your decision as the adopter, we do want to take due diligence and ensure that a homeowner approves of the dog that is to live on their property. It would be ideal to bring all family members in the home to the appointment, as the dog would be living alongside them and should demonstrate comfort them prior to making a final decision.\n
You may review our adoption policies and schedule an appointment at this website:\n""" + plain_url + """\n
Your authorization code is: """ + str(adopter.auth_code) + """. You'll need this when you set up your appointment.\n
Thank you,
The Adoptions Team\n
Saving Grace Animals for Adoption
"""

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>Your Saving Grace adoption request has been reviewed and approved.</p>
        <p>We did notice on your application that you live with your family. It is our policy to require at least one parent attend any appointment with you. While the choice of dog is ultimately your decision as the adopter, we do want to take due diligence and ensure that a homeowner approves of the dog that is to live on their property. It would be ideal to bring all family members in the home to the appointment, as the dog would be living alongside them and should demonstrate comfort them prior to making a final decision.</p>
        <p>""" + url + """</p>
        <p>Thank you,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

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
