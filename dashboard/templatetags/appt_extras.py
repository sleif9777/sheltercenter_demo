from django import template
from appt_calendar.models import Appointment
import datetime

register = template.Library()

@register.filter(name='alert_overdue')
def alert_overdue(appt):
    delta_from_today = (datetime.date.today() - appt.last_update_sent).days
    print(delta_from_today)

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
