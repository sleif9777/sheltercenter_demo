import datetime
import os

from django.contrib.auth.models import User

from appt_calendar.date_time_strings import *

def replacer(html, adopter, appt):
    print(appt)
    today = datetime.datetime.today()

    if str(os.environ.get('LOCALHOST')) == "1":
        base_name = 'localhost'
    else:
        base_name = 'sheltercenter.dog'

    try:
        adp_replacements = {
            '*ADP_AUTH*': str(adopter.auth_code),
            '*ADP_FNAME*': adopter.f_name,
            '*ADP_DOG*': adopter.chosen_dog,
        }

        if adopter.lives_with_parents == True:
            adp_replacements['*ADP_LIVES_W_PARENTS*'] = "You indicated on your application that you live with your family. It is our policy to require at least one parent attend your first appointment with you. While the choice of dog is ultimately your decision as the adopter, we do want to take due diligence and ensure that a homeowner approves of the dog that is to live on their property. It would be ideal to bring all family members in the home to the appointment, as the dog would be living alongside them and should demonstrate comfort with them prior to making a final decision."
        else:
            adp_replacements['*ADP_LIVES_W_PARENTS*'] = ""
    except Exception as e:
        adp_replacements = {}

    try:
        apt_replacements = {}

        if appt != None:
            apt_replacements = {
                '*APT_DATE*': date_str(appt.date),
                '*APT_DOG*': appt.dog,
                '*APT_TIME*': time_str(appt.time),
            }
        else:
            appt_replacements = {
                '*APT_DOG*': appt.dog
            }

        if appt.appt_type == "5":
            apt_replacements['*APT_TYPE*'] = "adoption"
        elif appt.appt_type == "6":
            apt_replacements['*APT_TYPE*'] = "foster-to-adopt (FTA)"
    except Exception as f:
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

    try:
        html = html.replace('*SIGNATURE*', request.user.profile.signature)
    except:
        base_user = User.objects.get(username='base')
        html = html.replace('*SIGNATURE*', base_user.profile.signature)

    return html
