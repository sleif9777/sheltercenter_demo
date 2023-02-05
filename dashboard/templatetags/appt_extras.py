import datetime

from django import template

from appt_calendar.models import Appointment

register = template.Library()

@register.filter(name='alert_overdue')
def alert_overdue(appt):
    delta_from_today = (datetime.date.today() - appt.last_update_sent).days

    if delta_from_today >= 7:
        return True
    else:
        return False


@register.filter(name='is_chosen')
def is_chosen(appt):
    if appt.outcome in ["3", "9", "10"]:
        return True

    return False


@register.filter(name='notes_only')
def notes_only(appt):
    if appt.appt_type in ["1", "2", "3"]:
        if appt.adopter:
            return False
        else:
            return True

    return False


@register.filter(name='show_notes')
def show_notes(appt: Appointment):
    show = False

    try:
        # for appts in schedulable, should be shown so long as at least one exists
        if appt.internal_notes or appt.adopter_notes:
            show = True
        # for non-schedulable, should be shown so long as one exists other than app_interest
        if appt.schedulable() and appt.adopter.app_interest:
            show = True
    except:
        pass

    return show


@register.filter(name='show_watchlist')
def show_watchlist(appt, list_type):
    available_list = appt.adopter.watchlist_available_str()
    unavailable_list = appt.adopter.watchlist_unavailable_str()

    match list_type:
        case "available":
            return True if available_list else False
        case "unavailable":
            return True if unavailable_list else False
        case "either":
            return True if available_list or unavailable_list else False
        case "both":
            return True if available_list and unavailable_list else False


@register.filter(name='pending_or_complete')
def pending_or_complete(adopter):
    waiting_for_chosen = adopter.waiting_for_chosen
    adoption_complete = adopter.adoption_complete

    try:
        chosen_appointment = Appointment.objects.get(
            adopter=adopter,
            outcome__in=["3", "9", "10"],
        )
    except:
        chosen_appointment = None

    if waiting_for_chosen and chosen_appointment:
        return "pending"
    elif waiting_for_chosen or adoption_complete:
        return "complete"
    else:
        return "none"