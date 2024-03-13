import json
from django import template
from store_app import settings
from store_app.api.models import Cart
from store_app.api.serializer import CartSerializer
from rest_framework.renderers import JSONRenderer


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
def list_length(value):
    return len(value)

@register.filter()
def get_gateway_url(value):
    return settings.GATEWAY_BASE_URL

@register.filter()
def get_user_image(value):
    user = json.loads(value)
    return user.get('avatarUrl', 'https://cdn-icons-png.flaticon.com/512/666/666201.png')

@register.filter()
def is_user_image(value):
    user = json.loads(value)
    if user.get('avatarUrl', None):
        return True 
    return False

@register.filter()
def tag_value(value):
    with open(f'./store_app/core/htmx-operation/operation-{value}.txt', 'w') as file:
        file.write(value)
    return value

@register.filter()
def promotion_expiration_date(value):
    value = value.strftime("%Y-%m-%d %H:%M:%S").split(" ")[0]
    return value

@register.filter()
def get_cart_items_count(value):
    cart = Cart.objects.get(id=value) 
    serializer = CartSerializer(cart)
    cart_data = JSONRenderer().render(serializer.data)
    cart_data = json.loads(cart_data)
    return cart_data.get("items_count", None)

@register.filter()
def get_cart_total_price(value):
    cart = Cart.objects.get(id=value) 
    serializer = CartSerializer(cart)
    cart_data = JSONRenderer().render(serializer.data)
    cart_data = json.loads(cart_data)
    return cart_data.get("total_price_after_discount", None)