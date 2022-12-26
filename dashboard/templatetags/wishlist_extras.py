from django import template

from adopter.models import Adopter
from appt_calendar.date_time_strings import *

register = template.Library()

@register.filter(name='on_wishlist')
def on_wishlist(dog, user_wishlist):
    return True if dog in user_wishlist else False


def calc_popularity(dog):
    wishlist_count = Adopter.objects.filter(wishlist__id=dog.id)
    return True if len(wishlist_count) > 10 else False


@register.filter(name='wishlist_class')
def wishlist_class(dog, date):
    # Dogs no longer available
    if dog.shelterluv_status != "Available for Adoption":
        return "strikethrough-italic"


@register.filter(name='wishlist_str')
def wishlist_str(dog, date):
    popular = calc_popularity(dog)
    string = ""

    if dog.shelterluv_status != "Available for Adoption":
        string += " - no longer available"
    
    if dog.offsite:
        if dog.appt_only:
            string += " - by appointment only, contact us to coordinate"
        else:
            if dog.foster_date > date or dog.host_date > date:
                potential_dates = [dog.foster_date, dog.host_date]
                rtrn_date = [date for date in potential_dates if date.year > 2000]
                string += " - not available on this date, returning {0}".format(
                    date_num_str(rtrn_date[0]))
            else:
                string += "*"
    else:
        string += "*"
        if popular:
            string += " - high interest, likely to be adopted quickly"

    return string


