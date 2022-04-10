from appt_calendar.date_time_strings import *
import os, datetime

def replacer(html, adopter, appt):
    today = datetime.datetime.today()

    if str(os.environ.get('LOCALHOST')) == "1":
        base_name = 'localhost'
    else:
        base_name = 'sheltercenter.dog'

    cancel_url = '<a href="http://{0}/">Click here to cancel your appointment.</a>'

    home_url = '<a href="http://{0}/">Click here to schedule or reschedule your appointment.</a>'

    try:
        adp_replacements = {
            '*ADP_AUTH*': str(adopter.auth_code),
            '*ADP_FNAME*': adopter.adopter_first_name,
            '*ADP_DOG*': adopter.chosen_dog,
            '*ADP_HOME_URL*': home_url.format(base_name, adopter.id)
        }

        if adopter.lives_with_parents == True:
            adp_replacements['*ADP_LIVES_W_PARENTS*'] = "You indicated on your application that you live with your family. It is our policy to require at least one parent attend your first appointment with you. While the choice of dog is ultimately your decision as the adopter, we do want to take due diligence and ensure that a homeowner approves of the dog that is to live on their property. It would be ideal to bring all family members in the home to the appointment, as the dog would be living alongside them and should demonstrate comfort with them prior to making a final decision."
        else:
            adp_replacements['<p>*ADP_LIVES_W_PARENTS*</p>'] = ""

        if adopter.has_current_appt:
            adp_replacements['<p>You can reschedule your appointment here: *ADP_HOME_URL*</p>'] = home_url.format(base_name, adopter.id)
        else:
            adp_replacements['<p>You can reschedule your appointment here: *ADP_HOME_URL*</p>'] = ""
    except:
        adp_replacements = {}

    try:
        apt_replacements = {
            '*APT_DATE*': date_str(appt.date),
            '*APT_DOG*': appt.dog,
            '*APT_TIME*': time_str(appt.time),
        }

        if appt.appt_type == "5":
            apt_replacements['*APT_TYPE*'] = "adoption"
        elif appt.appt_type == "6":
            apt_replacements['*APT_TYPE*'] = "foster-to-adopt (FTA)"

        if adopter.has_current_appt:
            apt_replacements['*ADP_CANCEL_URL*'] = cancel_url.format(base_name, adopter.id, appt.id, appt.date.year, appt.date.month, appt.date.day)
        else:
            apt_replacements['<p>You can cancel your appointment here: *ADP_CANCEL_URL*</p>'] = ""
    except:
        apt_replacements = {}

    global_replacements = {
        '*HOST_URL*': '<a href="https://savinggracenc.org/host-a-dog/">If you would like to learn more about our Weekend Host program, please visit our website.</a>'
    }

    if today.weekday() >= 4:
        next_business_day = 0
        global_replacements['*NEXT_BUS_DAY*'] = "Monday"
    else:
        next_business_day = today.weekday() + 1
        global_replacements['*NEXT_BUS_DAY*'] = "tomorrow"

    if next_business_day == 2:
        global_replacements['*NEXT_BUS_DAY_OPEN*'] = next_bd_open(13, 0)
    else:
        global_replacements['*NEXT_BUS_DAY_OPEN*'] = next_bd_open(12, 0)

    replacements_master = {
        adopter: adp_replacements,
        appt: apt_replacements,
        'global': global_replacements,
    }

    for item in replacements_master:
        if item != None:
            for key in replacements_master[item]:
                if key in html:
                    html = html.replace(key, replacements_master[item][key])

    return html