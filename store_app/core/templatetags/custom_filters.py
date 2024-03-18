import json
from datetime import datetime
from django import template
from rest_framework.renderers import JSONRenderer
from store_app import settings
from store_app.api.models import Cart
from store_app.api.serializer import CartSerializer
from store_app.clients.notification import Notification
from store_app.tools.helpers import *


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
def get_notification_url(value):
    return settings.NOTIFICATION_BASE_URL

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
def round_number(value, digit):
    return round(value, digit)

@register.filter()
def division(value, value2):
    return value/value2

@register.filter()
def format_relative_time(value):
    input_date = datetime.fromisoformat(value[:-1]) if isinstance(value, str) else value
    current_date = datetime.now()

    time_difference = current_date - input_date
    seconds_difference = int(time_difference.total_seconds())
    minutes_difference = seconds_difference // 60
    hours_difference = minutes_difference // 60
    days_difference = hours_difference // 24
    months_difference = days_difference // 30.44
    years_difference = months_difference // 12

    if years_difference > 0:
        return f"{years_difference} year{'s' if years_difference != 1 else ''} ago"
    elif months_difference > 0:
        return f"{months_difference} month{'s' if months_difference != 1 else ''} ago"
    elif days_difference > 0:
        return f"{days_difference} day{'s' if days_difference != 1 else ''} ago"
    elif hours_difference > 0:
        return f"{hours_difference} hour{'s' if hours_difference != 1 else ''} ago"
    elif minutes_difference > 0:
        return f"{minutes_difference} minute{'s' if minutes_difference != 1 else ''} ago"
    else:
        return f"{seconds_difference} second{'s' if seconds_difference != 1 else ''} ago"

@register.filter()
def get_cart_items_count(value):
    try:
        cart = Cart.objects.get(id=value) 
        serializer = CartSerializer(cart)
        cart_data = JSONRenderer().render(serializer.data)
        cart_data = json.loads(cart_data)
        return cart_data.get("items_count", None)
    except:
        return 0

@register.filter()
def get_cart_total_price(value):
    try:
        cart = Cart.objects.get(id=value) 
        serializer = CartSerializer(cart)
        cart_data = JSONRenderer().render(serializer.data)
        cart_data = json.loads(cart_data)
        return cart_data.get("total_price_after_discount", None)
    except:
        return 0

@register.filter()
def get_user_notifications(value, value2):
    try:
        token = value
        user = value2
        user_email = json.loads(user).get('email')
        logger.info(f"Getting notifications for user: {user_email}")
        notification = Notification()
        notification.token = token

        user_notifications : list = notification.get_user_notifications(email=user_email)
        user_notifications = [notification for notification in user_notifications if not notification.get('seen')]
        user_notifications.sort(key=lambda x: x['createdAt'], reverse=True)

        return user_notifications[0:5]
    except Exception as e:
        logger.error(f"Error getting user notifications: {e}")
        return []
    
@register.filter()
def get_user_notifications_count(value, value2):
    try:
        token = value
        user = value2
        user_email = json.loads(user).get('email')
        logger.info(f"Getting notifications count for user: {user_email}")
        notification = Notification()
        notification.token = token

        user_notifications = notification.get_user_notifications(email=user_email)
        user_notifications = [notification for notification in user_notifications if not notification.get('seen')]
        return len(user_notifications)
    except:
        return 0

@register.filter()
def get_user_all_notifications_count(value, value2):
    try:
        token = value
        user = value2
        user_email = json.loads(user).get('email')
        logger.info(f"Getting notifications count for user: {user_email}")
        notification = Notification()
        notification.token = token

        user_notifications = notification.get_user_notifications(email=user_email)
        return len(user_notifications)
    except:
        return 0
    
@register.filter()
def delete_notification(value, value2):
    try:
        token = value
        notification_id = value2

        notification = Notification()
        notification.token = token

        notification.delete_notification(notification_id=notification_id)

        return None
    except Exception as e:
        logger.error(f"Error getting user notifications: {e}")
        return None