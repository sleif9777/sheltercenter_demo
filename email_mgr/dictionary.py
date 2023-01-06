import datetime
import os

from django.contrib.auth.models import User

from appt_calendar.date_time_strings import *
from dashboard.templatetags.wishlist_extras import calc_popularity

today = datetime.datetime.today()

def get_adopter_replacements(adopter, appt):
    adopter_replacements = {}
    lwp_text = "You indicated on your application that you live with your family. It is our policy to require at least one parent attend your first appointment with you. While the choice of dog is ultimately your decision as the adopter, we do want to take due diligence and ensure that a homeowner approves of the dog that is to live on their property. It would be ideal to bring all family members in the home to the appointment, as the dog would be living alongside them and should demonstrate comfort with them prior to making a final decision."

    try:
        adopter_replacements = {
            '*ADP_AUTH*': str(adopter.auth_code),
            '*ADP_DOG*': adopter.chosen_dog,
            '*ADP_FNAME*': adopter.f_name,
            '*ADP_LIVES_W_PARENTS*': lwp_text if adopter.lives_with_parents else "",
            '*ADP_WATCHLIST*': get_watchlist_replacements(adopter, appt.date)
        }
    except Exception as e:
        print(e)
        pass

    return adopter_replacements


def get_appt_replacements(appt):
    if appt:
        appt_replacements = {
            '*APT_DATE*': date_str(appt.date),
            '*APT_DOG*': appt.dog,
            '*APT_TIME*': time_str(appt.time),
        }

        if appt.appt_type == "5":
            appt_replacements['*APT_TYPE*'] = "adoption"
        elif appt.appt_type == "6":
            appt_replacements['*APT_TYPE*'] = "foster-to-adopt (FTA)"

    return appt_replacements


def get_next_bd_replacements():
    global today

    next_business_day = 0 if today.weekday() >= 4 else today.weekday() + 1
    next_business_day_text = "Monday" if today.weekday() >= 4 else "tomorrow"
    next_bd_open_hour = 13 if next_business_day == 3 else 12
    next_bd_replacements = {
        '*NEXT_BUS_DAY*': next_business_day_text,
        '*NEXT_BUS_DAY_OPEN*': next_bd_open(next_bd_open_hour, 0),
    }

    return next_bd_replacements


def get_signature():
    base_user = User.objects.get(username='base')
    return base_user.profile.signature  


def get_watchlist_replacements(adopter, date):
    statuses = ""
    foster_host_disclaimer = """
        <em><sup>**Fosters and hosts have first dibs to adopt their assigned dog, 
        if they choose to do so.</sup></em><br>
    """
    first_come_first_serve_disclaimer = """
        <em><sup>*Available on a first-come-first-serve basis. 
        Marking them on your watch list does not equate to any sort of 
        "hold" prior to an appointment.</sup></em><br>
    """
    inc_foster_host = False
    inc_first_come_first_serve = False

    for dog in adopter.wishlist.iterator():
        status = "*"
        popular = calc_popularity(dog)
        inc_first_come_first_serve = True

        if dog.shelterluv_status != "Available for Adoption":
            status = " - no longer available"

        if dog.offsite:
            if dog.foster_date > date or dog.host_date > date:
                potential_dates = [dog.foster_date, dog.host_date]
                rtrn_date = [date for date in potential_dates if date.year > 2000]
                status = " - in foster/extended host during your appointment on {0}, returning {1}**".format(
                    date_num_str(date), date_num_str(rtrn_date[0]))
                inc_foster_host = True
        elif popular:
                status = " - high interest, likely to be adopted quickly*"

        statuses += "{0}{1}<br>".format(dog.name, status)

    if inc_first_come_first_serve:
        statuses += first_come_first_serve_disclaimer

    if inc_foster_host:
        statuses += foster_host_disclaimer

    return statuses


def replacer(html, adopter, appt):
    global today

    adopter_replacements = get_adopter_replacements(adopter, appt)
    appt_replacements = get_appt_replacements(appt)
    next_bd_replacements = get_next_bd_replacements()

    global_replacements = {
        '*HOST_URL*': '<a href="https://savinggracenc.org/host-a-dog/">If you would like to learn more about our Weekend Host program, please visit our website.</a>',
        '*SIGNATURE*': get_signature()
    }

    replacements_master = {
        'adopter': adopter_replacements,
        'appt': appt_replacements,
        'global': global_replacements,
        'next_bd': next_bd_replacements
    }

    for item in replacements_master:
        if item:
            for key in replacements_master[item]:
                if key in html:
                    html = html.replace(key, replacements_master[item][key])

    return html
