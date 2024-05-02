from django.urls import path

from . import consumers

core_app_websocket_urlpatterns = [
    path("ws/notifications/", consumers.NotificationConsumer.as_asgi()),
]