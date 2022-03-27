from appt_calendar.date_time_strings import *
import os

def replacer(html, adopter, appt):
    if os.environ.get('LOCALHOST'):
        base_name = 'localhost'
    else:
        base_name = 'sheltercenter.dog'

    cancel_url = '<a href="http://{0}/calendar/adopter/cancel/adopter/{1}/appt/{2}/date/{3}/{4}/{5}/">Click here to cancel your appointment.</a>'

    home_url = '<a href="http://{0}/adopter/{1}/">Click here to schedule or reschedule your appointment.</a>'

    try:
        adp_replacements = {
            '*ADP_AUTH*': str(adopter.auth_code),
            '*ADP_FNAME*': adopter.adopter_first_name,
            '*ADP_HOME_URL*': home_url.format(base_name, adopter.id),
        }

        if adopter.lives_with_parents == True:
            adp_replacements['*ADP_LIVES_W_PARENTS*'] = "You indicated on your application that you live with your family. It is our policy to require at least one parent attend your first appointment with you. While the choice of dog is ultimately your decision as the adopter, we do want to take due diligence and ensure that a homeowner approves of the dog that is to live on their property. It would be ideal to bring all family members in the home to the appointment, as the dog would be living alongside them and should demonstrate comfort with them prior to making a final decision."
        else:
            adp_replacements['<p>*ADP_LIVES_W_PARENTS*</p>'] = ""

    except:
        adp_replacements = {}

    try:
        apt_replacements = {
            '*ADP_CANCEL_URL*': cancel_url.format(base_name, adopter.id, appt.id, appt.date.year, appt.date.month, appt.date.day),
            '*APT_DATE*': date_str(appt.date),
            '*APT_DOG*': appt.dog,
            '*APT_TIME*': time_str(appt.time),
        }

        if appt.appt_type == "5":
            apt_replacements['*APT_TYPE*'] = "adoption"
        elif appt.appt_type == "6":
            apt_replacements['*APT_TYPE*'] = "foster-to-adopt (FTA)"
    except:
        apt_replacements = {}

    global_replacements = {
        '*HOST_URL*': '<a href="https://savinggracenc.org/host-a-dog/">If you would like to learn more about our Weekend Host program, please visit our website.</a>'

    }

    replacements_master = {
        adopter: adp_replacements,
        appt: apt_replacements,
        'global': global_replacements
    }

    for item in replacements_master:
        print(replacements_master[item])
        if item != None:
            print(item)
            for key in replacements_master[item]:
                if key in html:
                    print(key)
                    html = html.replace(key, replacements_master[item][key])

    return html
