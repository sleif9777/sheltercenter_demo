import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from . import email_template

def send_email(time, date, adopter_first_name, adopter_full_name, adopter_email, msg_type):
    if date != None and time != None:
        date = date.strftime("%A, %#m/%#d")
        time = time.strftime("%#I:%M%p")

    sender_email = "sheltercenterdev@gmail.com"
    receiver_email = "sheltercenterdev+" + adopter_email + "@gmail.com"
    password = "Momo624!"

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message['Reply-To'] = "sheltercenterdev+sam@gmail.com"
    recipient_name = adopter_first_name

    # Create the plain-text and HTML version of your message


    # Turn these into plain/html MIMEText objects
    if msg_type == "confirm":
        text, html = email_template.confirm(time, date, recipient_name)
        message["Subject"] = "Your Appointment Has Been Confirmed: " + adopter_full_name
    elif msg_type == "cancel":
        text, html = email_template.cancel(time, date, recipient_name)
        message["Subject"] = "Your Appointment Has Been Cancelled: " + adopter_full_name
    elif msg_type == "reschedule":
        text, html = email_template.reschedule(time, date, recipient_name)
        message["Subject"] = "Your Appointment Has Been Rescheduled: " + adopter_full_name
    elif msg_type == "follow_up":
        text, html = email_template.follow_up(recipient_name)
        message["Subject"] = "Thank You For Visiting: " + adopter_full_name
    elif msg_type == "invite":
        url = "sheltercenter.dog/adopter/decision/" + adopter_email + "/"
        text, html = email_template.invite(recipient_name, url)
        message["Subject"] = "Your adoption request has been reviewed: " + adopter_full_name
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    #message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
