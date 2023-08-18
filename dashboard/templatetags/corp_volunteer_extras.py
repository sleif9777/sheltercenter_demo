from django import template
from django.contrib.auth.models import Group

from email_mgr.models import PendingMessage

register = template.Library()

@register.filter(name='able_to_confirm')
def able_to_confirm(event):
    return event.event_task and event.event_counselor