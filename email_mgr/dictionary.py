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
        }
        if appt:
            adopter_replacements['*ADP_WATCHLIST*'] = get_watchlist_replacements(
                adopter, appt.date)
    except Exception as e:
        pass

    return adopter_replacements


def get_appt_replacements(appt):
    appt_replacements = {}

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


def get_org_replacements(org):
    if org:
        org_replacements = {
            "*ORG_NAME*": org.org_name,
            "*ORG_L_FNAME*": org.leader_fname,
        }
    else:
        org_replacements = {}

    return org_replacements


def get_event_replacements(event):
    if event:
        event_replacements = {
            "*EVENT_COUNSELOR*": event.event_counselor,
            "*EVENT_DATE*": event.date_string(),
            "*EVENT_END*": time_str(event.event_end_time),
            "*EVENT_HEADCOUNT*": str(event.headcount) if event.headcount > 0 else "10",
            "*EVENT_START*": time_str(event.event_start_time),
            "*EVENT_TASK*": event.event_task,
            "*EVENT_WEEKDAY*": weekday_str(event.date),
        }
    else:
        event_replacements = {}

    return event_replacements

def get_litter_string(litter):
    dogs_in_litter = [dog.name for dog in litter.dogs.iterator()]
    dogs_in_litter_str = ", ".join(dogs_in_litter)

    if len(litter.name) > 0:
        return "our {0} litter ({1})".format(
            litter.name, dogs_in_litter_str
        )
    else:
        return "one of our litters ({0})".format(
            dogs_in_litter_str
        )


def get_litter_or_dog_replacements(litter, dog):
    if litter:
        return {
            "*DOGNAME*": get_litter_string(litter),
            "*DOGNAME2*": "This litter"
        }
    elif dog:
        return {
            "*DOGNAME*": dog.name,
            "*DOGNAME2*": dog.name
        }
    else:
        return {}


def get_signature():
    base_user = User.objects.get(username='base')
    return base_user.profile.signature


def evaluate_dog_for_watchlist_replacements(dog, date):
    status = "*"
    popular = calc_popularity(dog)
    is_foster_host = False

    if dog.shelterluv_status != "Available for Adoption":
        status = " - no longer available"

    if dog.offsite:
        if dog.appt_only:
            status = " - by appointment only, must be arranged by the Adoptions team in advance"
        elif dog.alter_date == date:
            status = " - in surgery and unavailable for meetings today"
        elif dog.foster_date > date or dog.host_date > date:
            potential_dates = [dog.foster_date, dog.host_date]
            rtrn_date = [date for date in potential_dates if date.year > 2000]
            status = " - in foster/extended host during your appointment on {0}, returning {1}**".format(
                date_num_str(date), date_num_str(rtrn_date[0]))
            is_foster_host = True
    elif popular:
            status = " - high interest, likely to be adopted quickly*"

    return status, is_foster_host

def get_watchlist_replacements(adopter, date):
    statuses = ""
    foster_host_disclaimer = """
        <em><sup>**Fosters and hosts have first dibs to adopt their assigned dog, 
        if they choose to do so.</sup></em><br>
    """
    first_come_first_serve_disclaimer = """
        <em><sup>*Currently available on a first-come-first-serve basis. 
        Marking them on your watch list does not equate to any sort of 
        "hold" prior to an appointment.</sup></em><br>
    """
    inc_foster_host = False
    watchlist = adopter.wishlist.iterator()

    for dog in watchlist:
        status, is_foster_host = evaluate_dog_for_watchlist_replacements(
            dog, date)

        if is_foster_host:
            inc_foster_host = True

        statuses += "{0}{1}<br>".format(dog.name, status)

    if adopter.wishlist.count() > 0:
        statuses += first_come_first_serve_disclaimer

    if inc_foster_host:
        statuses += foster_host_disclaimer

    return statuses


def replacer(html, adopter, appt, litter=None, dog=None, org=None, event=None):
    global today

    adopter_replacements = get_adopter_replacements(adopter, appt)
    appt_replacements = get_appt_replacements(appt)
    next_bd_replacements = get_next_bd_replacements()
    litter_or_dog_replacements = get_litter_or_dog_replacements(litter, dog)
    org_replacements = get_org_replacements(org)
    event_replacements = get_event_replacements(event)

    global_replacements = {
        '*HOST_URL*': '<a href="https://savinggracenc.org/host-a-dog/">If you would like to learn more about our Weekend Host program, please visit our website.</a>',
        '*SIGNATURE*': get_signature()
    }

    replacements_master = {
        'adopter': adopter_replacements,
        'appt': appt_replacements,
        'event': event_replacements,
        'global': global_replacements,
        'litter_or_dog': litter_or_dog_replacements,
        'next_bd': next_bd_replacements,
        'org': org_replacements,
    }

    for item in replacements_master:
        if item:
            for key in replacements_master[item]:
                if key in html:
                    html = html.replace(key, replacements_master[item][key])

    return html
