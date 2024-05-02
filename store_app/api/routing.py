# from django.urls import path

# from . import consumers

# api_app_websocket_urlpatterns = [
#     path("ws/socket_notifications/", consumers.NotificationConsumer.as_asgi()),
# ]

from django.urls import re_path

from . import consumers

api_app_websocket_urlpatterns = [
    re_path(r"ws/socket_notifications/", consumers.NotificationConsumer.as_asgi()),
]