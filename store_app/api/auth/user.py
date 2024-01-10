from store_app.api.middleware.auth_middleware import JWTAuthMiddleware
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            # JWTAuthMiddleware is already initialized by Django middleware and has set current_user to the request
            user_dict = request.current_user
            token = request.token

            if user_dict is None:
                return None

            # You can adapt this part based on the structure of your user dictionary
            user_id = user_dict.get('id')
            user_createdAt = user_dict.get('createdAt')
            user_updatedAt = user_dict.get('updatedAt')
            user_email = user_dict.get('email')
            user_username = user_dict.get('username')
            user_role = user_dict.get('role')
            user_phone = user_dict.get('phone')

            # Create a simple user object without saving to the database
            user = SimpleUser(user_id, user_createdAt, user_updatedAt, user_email, user_username, user_role, user_phone)

            return user, token
        except:
            return None, None

class SimpleUser:
    def __init__(self, user_id, createdAt, updatedAt, email, username, role, phone):
        self.id = user_id
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.email = email
        self.username = username
        self.role = role
        self.phone = phone
        self.is_staff = (role == 'ADMIN')

    def is_authenticated(self):
        return True