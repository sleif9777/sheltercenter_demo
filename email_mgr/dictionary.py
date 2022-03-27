from appt_calendar.date_time_strings import *
import os

def replacer(html, adopter, appt):
    if os.environ.get('LOCALHOST'):
        base_name = 'localhost'
    else:
        base_name = 'sheltercenter.dog'

    cancel_url = '<a href="http://{0}/calendar/adopter/cancel/adopter/{1}/appt/{2}/date/{3}/{4}/{5}/">Click here to cancel your appointment.</a>'

    reschedule_url = '<a href="http://{0}/adopter/{1}/">Click here to reschedule your appointment.</a>'

    replacements = {
        '*ADP_AUTH*': str(adopter.auth_code),
        '*ADP_CANCEL_URL*': cancel_url.format(base_name, adopter.id, appt.id, appt.date.year, appt.date.month, appt.date.day),
        '*ADP_FNAME*': adopter.adopter_first_name,
        '*ADP_RESCHED_URL*': reschedule_url.format(base_name, adopter.id),
        '*APT_DATE*': date_str(appt.date),
        '*APT_DOG*': appt.dog,
        '*APT_TIME*': time_str(appt.time),
    }

    if appt.appt_type == "5":
        replacements['*APT_TYPE*'] = "adoption"
    elif appt.appt_type == "6":
        replacements['*APT_TYPE*'] = "foster-to-adopt (FTA)"

    for key in replacements:
        if key in html:
            html = html.replace(key, replacements[key])

    return html
