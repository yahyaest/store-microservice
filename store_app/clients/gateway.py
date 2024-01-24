import requests
import json

from store_app import settings
from store_app.tools.helpers import *


class Gateway:
    def __init__(self) -> None:
        self.gateway_base_url = settings.GATEWAY_BASE_URL
        self.gateway_signin_url = f'{self.gateway_base_url}/api/auth/signin/'
        self.gateway_signup_url = f'{self.gateway_base_url}/api/auth/signup/'
        self.gateway_current_user_url = f'{self.gateway_base_url}/api/users/me/'
        self.gateway_images_url = f'{self.gateway_base_url}/api/images/'
        self.gateway_current_user_image_url = f'{self.gateway_base_url}/api/images/me/'
        self.token = None

    def register(self, data):
        try:
            token = None
            error =None

            headers = {}
            headers['Content-Type'] = 'application/json'

            payload = json.dumps(data)
            r = requests.post(self.gateway_signup_url, verify=False, data=payload, headers= headers)
            if r.status_code == 201:
                res = r.json()
                token = res['access_token']
                self.token = token
            else:
                logger.error("=====> register failed --> failed")
                logger.error(r.status_code)
                logger.error(r.text)
                error = json.loads(r.text)
            return token,error
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None,None

    def login(self, data):
        try:
            token = None
            error =None

            headers = {}
            headers['Content-Type'] = 'application/json'

            payload = json.dumps(data)
            r = requests.post(self.gateway_signin_url, verify=False, data=payload, headers= headers)
            if r.status_code == 200:
                res = r.json()
                token = res['access_token']
                self.token = token
            else:
                logger.error("=====> login failed --> failed")
                logger.error(r.status_code)
                logger.error(r.text)
                error = json.loads(r.text)
            return token,error
        except Exception as e:
            logger.error(f"Error logging user: {e}")
            return None,None

    def get_current_user(self):
        try:
            headers = {}
            headers['Content-Type'] = 'application/json'
            headers['Authorization'] = f'Bearer {self.token}'
            r = requests.get(self.gateway_current_user_url, verify=False, headers= headers)
            if r.status_code == 200:
                user = r.json()
                return user
            else:
                logger.error("=====> get current user failed --> failed")
                logger.error(r.status_code)
                logger.error(r.text)
            return None
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    def get_current_user_image(self):
        try:
            headers = {}
            headers['Content-Type'] = 'application/json'
            headers['Authorization'] = f'Bearer {self.token}'
            r = requests.get(self.gateway_current_user_image_url, verify=False, headers= headers)
            if r.status_code == 200:
                user_image = r.json()
                return user_image
            else:
                logger.error("=====> get current user image failed --> failed")
                logger.error(r.status_code)
                logger.error(r.text)
            return None
        except Exception as e:
            logger.error(f"Error getting current user image: {e}")
            return None

    def upload_image(self, image_file, username):
        try:
            data = None
            error =None

            headers = {}
            headers['Authorization'] = f'Bearer {self.token}'

            files = {'file': (image_file._name, image_file, image_file.content_type), 'username': (None, username)}

            r = requests.post(self.gateway_images_url, headers=headers, files=files)

            if r.status_code == 201:
                data = r.json()
            else:
                logger.error("=====> upload user image failed failed --> failed")
                logger.error(r.status_code)
                logger.error(r.text)
                error = json.loads(r.text)
            return data, error

        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None,None