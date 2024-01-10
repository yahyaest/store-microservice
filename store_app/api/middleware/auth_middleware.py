import os
import requests
import jwt
from django.http import JsonResponse
from django.conf import settings

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self.get_response:
            raise Exception("get_response not set in JWTAuthMiddleware")

        # Your JWT secret key
        jwt_secret = os.getenv("JWT_SECRET",None)

        # Get the JWT token from the Authorization header
        authorization_header = request.headers.get('Authorization', '')
        if not authorization_header.startswith('Bearer '):
            # return JsonResponse({'error': 'Unauthorized'}, status=401)
            # Continue processing the request
            response = self.get_response(request)
            return response

        token = authorization_header.split(' ')[1]

        try:
            # Decode the JWT token
            decoded_token = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            user_id = decoded_token['sub']
            # user_email = decoded_token['email']

            # Make a request to the gateway app
            gateway_base_url = settings.GATEWAY_BASE_URL
            gateway_users_url = f'{gateway_base_url}/api/users/{user_id}/'
            response = requests.get(gateway_users_url, headers={'Authorization': f'Bearer {token}'})
            current_user = response.json()
            current_user.pop('password')

            if response.status_code == 200:
                # Attach user data to the request
                request.current_user = current_user
                request.token = token
            else:
                return JsonResponse({'error': 'Unauthorized'}, status=401)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        # Continue processing the request
        response = self.get_response(request)
        return response
