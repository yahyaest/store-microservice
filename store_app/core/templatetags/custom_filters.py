import json
from django import template
from store_app import settings


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

@register.filter()
def get_gateway_url(value):
    return settings.GATEWAY_BASE_URL

@register.filter()
def get_user_image(value):
    user = json.loads(value)
    return user['avatarUrl']

@register.filter()
def tag_value(value):
    with open(f'./store_app/core/htmx-operation/operation-{value}.txt', 'w') as file:
        file.write(value)
    return value

