from django import template
register = template.Library()

@register.filter
def get_fields(obj):
    return obj._meta.get_fields()
