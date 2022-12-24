from django import template

register = template.Library()

@register.filter(name='on_wishlist')
def on_wishlist(dog, user_wishlist):
    return True if dog in user_wishlist else False




