import smtplib, ssl, datetime, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from appt_calendar.models import Appointment

def send_email(text, html, reply_to, subject, receiver_email):
    sender_email = "sheltercenterdev@gmail.com"
    password = "Momo624!"

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email

    if reply_to == "default":
        message['Reply-To'] = "sheltercenterdev+sam@gmail.com"
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
    time = time.strftime("%#I:%M%p")
    date = date.strftime("%A, %#m/%#d")

    return time, date

#def custom_msg(adopter, message, subject):

def alert_date_set(adopter, date):
    subject = "We'll Be In Touch Soon!"
    name = adopter.adopter_first_name
    email = adopter.adopter_email

    date_string = date.strftime("%A, %#m/%#d")

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

def dates_are_open(adopter, date):
    subject = "Let's Book Your Saving Grace Adoption Appointment!"
    name = adopter.adopter_first_name
    email = adopter.adopter_email

    plain_url = 'http://127.0.0.1:8000/calendar/adopter/' + str(adopter.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    url = '<a href="http://127.0.0.1:8000/calendar/adopter/' + str(adopter.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Click here to schedule your appointment.</a>'

    date_string = date.strftime("%A, %#m/%#d")

    text = """\
    Hi """ + name + """,\n
    We are now scheduling adoption appointments for """ + date_string + """.\n
    Visit this website to schedule your adoption appointment: """ + url + """\n
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
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def limited_matches(adopter, appt, description):
    print(description)
    if description == "lowshed":
        description = "low-shedding and/or hypoallergenic dogs"

    subject = "An Update About Your Saving Grace Appointment"
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    date = appt.date

    plain_reschedule_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    reschedule_url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">If you would prefer to reschedule your appointment, click here.</a>'

    plain_cancel_url = 'http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    cancel_url = '<a href="http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">If you would prefer to cancel your appointment, click here.</a>'

    if description in ["puppies", "small dogs"]:
        print("yes2!")
        text = """\
        Hi """ + name + """,\n
        We wanted to follow up with you as we see you have requested to meet """ + description + """.\n
        We are a little limited with available """ + description + """ at this time.\n
        We do encourage you to keep your appointment. There are always wonderful dogs for you to visit with and we always recommend keeping an open mind to see who may click with you. We also have dogs who have not had the chance to have photos taken and are not on our website yet.\n
        If you wish to reschedule your appointment, you can do so here: """ + plain_reschedule_url + """\n
        If you wish to cancel your appointment, you can do so here: """ + plain_cancel_url + """\n
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
        next_bd_opening_hour = datetime.time(13,0).strftime("%#I:%M%p").lower()
    else:
        next_bd_opening_hour = datetime.time(12,0).strftime("%#I:%M%p").lower()

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

    plain_reschedule_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    reschedule_url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">If you wish to reschedule your appointment, click here.</a>'

    plain_cancel_url = 'http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    cancel_url = '<a href="http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">If you wish to cancel your appointment, click here.</a>'

    text = """\
    Hi """ + name + """,\n
    We wanted to follow up as we see the following notes you provided for your upcoming appointment:\n""" + appt.adopter_notes + """\n
    The dog(s) you mentioned above have found their forever homes.\n
    While your first choices may no longer be available, we do encourage you to keep your appointment. We always have wonderful dogs for you to visit with and always recommend keeping an open mind to see who may click with you. We also have dogs who have not had the chance to have photos taken and are not on our website yet.\n
    If you wish to reschedule your appointment, you can do so here: """ + plain_reschedule_url + """\n
    If you wish to cancel your appointment, you can do so here: """ + plain_cancel_url + """\n
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
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def new_contact_adopter_msg(adopter, message, include_links):
    subject = "New Message From The Saving Grace Adoptions Team"
    name = adopter.adopter_first_name
    email = adopter.adopter_email

    plain_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">Manage Your Appointment Here</a>'

    if include_links == True:
        text = """\
        Hi """ + name + """,\n
        """ + message + """\n
        Visit this website to manage your adoption appointment: """ + plain_url + """\n
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
    subject = "New Message From " + adopter.adopter_full_name()
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
        plain_cancel_url = 'http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
        cancel_url = '<a href="http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Cancel Appointment</a>'
        plain_reschedule_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
        reschedule_url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">Reschedule Appointment</a>'

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
        plain_schedule_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
        schedule_url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">Schedule Appointment</a>'

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

def confirm(time, date, adopter, appt):
    subject = "Your Appointment Has Been Confirmed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    plain_reschedule_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    reschedule_url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">Click here to reschedule your appointment.</a>'

    plain_cancel_url = 'http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    cancel_url = '<a href="http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Click here to cancel your appointment.</a>'

    time, date = clean_time_and_date(time, date)

    text = """\
    Appointment Confirmation\n
    Hi """ + name + """,\n
    You have been added to our schedule for """ + time + """ on """ + date + """.\n
    You can reschedule your appointment here: """ + plain_reschedule_url + """\n
    You can cancel your appointment here: """ + plain_cancel_url + """\n
    It is important that you read the Visiting Instructions included below before you arrive for your appointment, as well as those in your original approval email. Our adoption policies and expectations, as well as the answers to many of our frequently asked questions, are provided here.\n
    We are continuing to follow CDC Guidelines for COVID. All visits take place outdoors, and we are a mask-optional venue that will respect your decisions based on your comfort level. Please know that our Adoptions Team has been vaccinated. We look forward to meeting you.\n
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
        <p>You have been added to our schedule for """ + time + """ on """ + date + """.</p>
        <p>""" + reschedule_url + """</p>
        <p>""" + cancel_url + """</p>
        <p>It is important that you read the Visiting Instructions included below before you arrive for your appointment, as well as those in your original approval email. Our adoption policies and expectations, as well as the answers to many of our frequently asked questions, are provided here.</p>
        <p>We are continuing to follow CDC Guidelines for COVID. All visits take place outdoors, and we are a mask-optional venue that will respect your decisions based on your comfort level. Please know that our Adoptions Team has been vaccinated. We look forward to meeting you.</p>
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
    print("done")

def adoption_paperwork(time, date, adopter, appt, hw_status):
    if hw_status == False:
        subject = "Your Final Adoption Appointment Has Been Confirmed: " + adopter.adopter_full_name().upper()
        appt_type = "adoption"
    else:
        subject = "Your FTA Appointment Has Been Confirmed: " + adopter.adopter_full_name().upper()
        appt_type = "foster-to-adopt (FTA)"
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    dog = appt.dog
    time, date = clean_time_and_date(time, date)

    text = """\
    Appointment Confirmation\n
    Hi """ + name + """,\n
    You have been added to our schedule for """ + time + """ on """ + date + """ to complete the """ + appt_type + """ paperwork for """ + dog + """.\n
    Please review the Visiting Instructions included below before you arrive for your appointment.\n
    We are continuing to follow CDC Guidelines for COVID. All visits take place outdoors, and we are a mask-optional venue that will respect your decisions based on your comfort level. Please know that our Adoptions Team has been vaccinated. We look forward to seeing you soon.\n
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
    """

    html = """\
    <html>
      <body>
        <h2>Appointment Confirmation</h2>
        <p>Hi """ + name + """,</p>
        <p>You have been added to our schedule for """ + time + """ on """ + date + """ to complete the """ + appt_type + """ paperwork for """ + dog + """.</p>
        <p>Please review the Visiting Instructions included below before you arrive for your appointment.</p>
        <p>We are continuing to follow CDC Guidelines for COVID. All visits take place outdoors, and we are a mask-optional venue that will respect your decisions based on your comfort level. Please know that our Adoptions Team has been vaccinated. We look forward to seeing you soon.</p>
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
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)
    print("done")

def cancel(time, date, adopter):
    subject = "Your Appointment Has Been Cancelled"
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    time, date = clean_time_and_date(time, date)

    plain_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">If you wish to reschedule at any time, you may do so by clicking here.</a>'

    text = """\
    Appointment Cancelled\n
    Hi """ + name + """,\n
    Your appointment for """ + time + """ on """ + date + """ has been cancelled.\n
    Your adoption request is valid for one year. If you wish to reschedule at any time, you may do so using this website: """ + url + """\n
    All the best, \n
    The Adoptions Team
    Saving Grace Animals for Adoption
    """

    html = """\
    <html>
      <body>
        <h2>Appointment Cancelled</h2>
        <p>Hi """ + name + """,</p>
        <p>Your appointment for """ + time + """ on """ + date + """ has been cancelled.</p>
        <p>Your adoption request is valid for one year. """ + url + """</p>
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def reschedule(time, date, adopter, appt):
    subject = "Your Appointment Has Been Rescheduled: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    plain_reschedule_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    reschedule_url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">Click here to reschedule your appointment.</a>'

    plain_cancel_url = 'http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    cancel_url = '<a href="http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Click here to cancel your appointment.</a>'

    time, date = clean_time_and_date(time, date)

    text = """\
    Appointment Rescheduled\n
    Hi """ + name + """,\n
    Your appointment has been rescheduled for """ + time + """ on """ + date + """.\n
    You can reschedule your appointment here: """ + plain_reschedule_url + """\n
    You can cancel your appointment here: """ + plain_cancel_url + """\n
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
    subject = "Your Follow-Up Appointment Has Been Scheduled: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    plain_reschedule_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    reschedule_url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">Click here to reschedule your appointment.</a>'

    plain_cancel_url = 'http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
    cancel_url = '<a href="http://127.0.0.1:8000/cancel/adopter/' + str(adopter.id) + '/appt/' + str(appt.id) + '/date/' + str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/">Click here to cancel your appointment.</a>'

    time, date = clean_time_and_date(time, date)

    text = """\
    Appointment Rescheduled\n
    Hi """ + name + """,\n
    Your follow-up appointment has been scheduled for """ + time + """ on """ + date + """.\n
    You can reschedule your appointment here: """ + plain_reschedule_url + """\n
    You can cancel your appointment here: """ + plain_cancel_url + """\n
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

def follow_up(adopter):
    subject = "Thank You For Visiting: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    plain_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">If you would like to schedule another appointment, click here.</a>'

    text = """\
    Hi """ + name + """,\n
    Thank you for visiting the Funny Farm today!\n
    We are sorry we were not able to match you with anyone today. There are always great dogs entering our program, and your new best friend may be here soon! If you would like to schedule another appointment, visit this website:\n""" + plain_url + """\n
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
        <p>We hope to welcome you back soon.</p
        <p>All the best,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def follow_up_w_host(adopter):
    subject = "Thank You For Visiting: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    plain_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">If you would like to schedule another appointment, click here.</a>'

    plain_host_url = 'https://savinggracenc.org/host-a-dog/'
    host_url = '<a href="https://savinggracenc.org/host-a-dog/">If you would like to learn more about our Weekend Host program, click here.</a>'

    text = """\
    Hi """ + name + """,\n
    Thank you for visiting the Funny Farm today!\n
    We are sorry we were not able to match you with anyone today. There are always great dogs entering our program, and your new best friend may be here soon! If you would like to schedule another appointment, visit this website:\n""" + plain_url + """\n
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
    plain_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">You may review our response by clicking here.</a>'

    text = """\
Hi """ + name + """,\n
Your Saving Grace adoption request has been reviewed. You may review our response here:\n""" + plain_url + """\n
If you are a current foster or host who is adopting your foster/host dog, please respond directly to this email so we can proceed accordingly.\n
Thank you,
The Adoptions Team\n
Saving Grace Animals for Adoption
"""

    html = """\
    <html>
      <body>
        <p>Hi """ + name + """,</p>
        <p>Your Saving Grace adoption request has been reviewed. """ + url + """</p>
        <p>If you are a current foster or host who is adopting your foster/host dog, please respond directly to this email so we can proceed accordingly.</p>
        <p>Thank you,<br>The Adoptions Team<br>Saving Grace Animals for Adoption</p>
      </body>
    </html>
    """

    send_email(text, html, "default", subject, email)

def invite_oos(adopter, url):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name

    plain_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">After reading these special expectations for long-distance adoption, you may click here to continue forward in our process, review our standard adoption expectations, and schedule an appointment.</a>'

    text = """\
Hi """ + name + """,\n
Thank you for considering adoption through Saving Grace in North Carolina where we always have great dogs waiting for homes.\n
We are happy to help out of state adopters and want to provide appropriate expectations for long-distance adoption. We do not ship or offer transport for adopted dogs. Each adopter must visit with an animal in person and commit to following through with adoption. In order to give the most dogs an opportunity for a forever family, dogs are not placed on hold. This means a dog you are considering may be adopted before your visit. It is best to visit with an open mind and choose a dog in person that best fits what you are looking for rather than be set on adopting a specific dog on the website.\n
If a dog has not completed their veterinary care, an additional trip may be necessary at a later date to complete the adoption and pick up the dog. This process will vary with each animal and their medical needs. It is best to check with your veterinarian in your state of residence regarding health certificates/licensing required when bringing a new animal into your state. It is up to adopters to acquire the health certificate from a North Carolina veterinarian. While we can recommend veterinarians, we are unable to provide this service.\n
After reading these special expectations for long-distance adoption, you may continue to review our standard adoption expectations and schedule an appointment here: \n""" + plain_url + """\n
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

def invite_lives_w_parents(adopter, url):
    subject = "Your adoption request has been reviewed: " + adopter.adopter_full_name().upper()
    email = adopter.adopter_email
    name = adopter.adopter_first_name
    plain_url = 'http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/'
    url = '<a href="http://127.0.0.1:8000/adopter/' + str(adopter.id) + '/">You may review our adoption policies and schedule an appointment by clicking here.</a>'

    text = """\
Hi """ + name + """,\n
Your Saving Grace adoption request has been reviewed and approved.\n
We did notice on your application that you live with your family. It is our policy to require at least one parent attend any appointment with you. While the choice of dog is ultimately your decision as the adopter, we do want to take due diligence and ensure that a homeowner approves of the dog that is to live on their property. It would be ideal to bring all family members in the home to the appointment, as the dog would be living alongside them and should demonstrate comfort them prior to making a final decision.\n
You may review our adoption policies and schedule an appointment at this website:\n""" + plain_url + """\n
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
