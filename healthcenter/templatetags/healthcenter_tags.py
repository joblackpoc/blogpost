from django import template
register = template.Library()

@register.filter
def get_field(obj, field):
    return getattr(obj, field, '')
