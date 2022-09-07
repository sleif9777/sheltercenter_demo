from django import template
from django.contrib.auth.models import Group

from email_mgr.models import PendingMessage

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)

    print(group, user.groups.all())

    if group in user.groups.all():
        return True

    return False


@register.filter(name='show_calendar')
def show_calendar(user, visible):

    print(visible)

    if has_group(user, "adopter"):
        if user.adopter.adoption_complete or user.adopter.waiting_for_chosen:
            return False
        if not visible:
            return False
    
    print('t')

    return True


@register.filter(name='outbox_count')
def outbox_count(s):
    return len(list(PendingMessage.objects.all()))
