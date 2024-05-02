"""
ASGI config for store project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from store_app.core.routing import core_app_websocket_urlpatterns
from store_app.api.routing import api_app_websocket_urlpatterns
from store_app.tools.helpers import logger

websocket_urlpatterns = core_app_websocket_urlpatterns + api_app_websocket_urlpatterns

logger.info(f"websocket_urlpatterns is : {websocket_urlpatterns}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store_app.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": application,
    "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
})