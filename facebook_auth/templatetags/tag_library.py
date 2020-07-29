from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter()
def to_int(value):
    return int(value)

@register.filter()
def to_float(value):
    return float(value)

@register.filter()
def to_string(value):
    return str(value)

@register.filter()
@stringfilter
def upper(value):
    return value.upper()