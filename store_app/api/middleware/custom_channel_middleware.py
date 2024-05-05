import os
import jwt
from django.conf import settings
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.sessions import CookieMiddleware, SessionMiddleware
from channels.auth import UserLazyObject
from store_app.clients.gateway import Gateway
from store_app.tools.helpers import logger
from urllib.parse import parse_qs           


@database_sync_to_async
def get_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    # postpone model import to avoid ImproperlyConfigured error before Django
    # setup is complete.
    from django.contrib.auth.models import AnonymousUser
    token = None
    user = None
    try:
        query_params = parse_qs(scope['query_string'].decode('utf-8'))
        token = query_params.get('token', None)[0]
        jwt_secret = os.getenv("JWT_SECRET",None)
        decoded_token = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        user_email = decoded_token['email']
        data = {"email":settings.STORE_USERNAME,"password": settings.STORE_PASSWORD}
        gateway = Gateway()
        gateway.login(data)
        user = gateway.get_user_by_email(user_email)
        user.pop('password')        

    except Exception as e:
        logger.error(f"Error getting user: {e}")
        
    return user or AnonymousUser()

    
class CustomAuthMiddleware(BaseMiddleware):
    """
    Middleware which populates scope["user"] from a Django session.
    Requires SessionMiddleware to function.
    """

    def populate_scope(self, scope):
        # Make sure we have a session
        if "session" not in scope:
            raise ValueError(
                "AuthMiddleware cannot find session in scope. "
                "SessionMiddleware must be above it."
            )
        # Add it to the scope if it's not there already
        if "user" not in scope:
            scope["user"] = UserLazyObject()

    async def resolve_scope(self, scope):
        scope["user"]._wrapped = await get_user(scope)

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        # Scope injection/mutation per this middleware's needs.
        self.populate_scope(scope)
        # Grab the finalized/resolved scope
        await self.resolve_scope(scope)

        return await super().__call__(scope, receive, send)


# Handy shortcut for applying all three layers at once
def CustomAuthMiddlewareStack(inner):
    return CookieMiddleware(SessionMiddleware(CustomAuthMiddleware(inner)))