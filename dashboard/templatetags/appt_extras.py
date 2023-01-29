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
def show_notes(appt):
    show = False

    try:
        # for appts in schedulable, should be shown so long as at least one exists
        if appt.internal_notes or appt.adopter_notes:
            show = True
        # for non-schedulable, should be shown so long as one exists other than app_interest
        if appt.appt_type in ["1", "2", "3"] and appt.adopter.app_interest:
            show = True
    except:
        pass

    return show


@register.filter(name='pending_or_complete')
def pending_or_complete(adopter):
    waiting_for_chosen = adopter.waiting_for_chosen
    chosen_appointment = Appointment.objects.get(
        adopter=adopter,
        status__in=["3", "9", "10"],
    )

    if waiting_for_chosen and chosen_appointment:
        return "pending"
    elif waiting_for_chosen:
        return "complete"
    else:
        return