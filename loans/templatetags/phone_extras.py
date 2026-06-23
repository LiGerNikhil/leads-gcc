import re
from django import template

register = template.Library()

@register.filter
def digits_only(value):
    if not value:
        return ''
    return re.sub(r'\D', '', str(value))

@register.filter
def tel_link(value):
    d = digits_only(value)
    return f'tel:+91{d}' if d else '#'

@register.filter
def wa_link(value):
    d = digits_only(value)
    return f'https://wa.me/91{d}' if d else '#'