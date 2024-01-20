from django import template
from django.http import QueryDict


register = template.Library()

@register.filter()
def replace(value, args):
    old = args.split(",")[0]
    new = args.split(",")[1]
    return value.replace(old, new)


@register.filter()
def split(value, arg):
    return value.split(arg)

@register.filter()
def list_to_string(value):
    return ', '.join(value)


