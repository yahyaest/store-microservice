import requests
import json

from store_app import settings
from store_app.tools.helpers import *


class Gateway:
    def __init__(self) -> None:
        self.gateway_base_url = settings.GATEWAY_BASE_URL
        self.gateway_signin_url = f'{self.gateway_base_url}/api/auth/signin/'
        self.gateway_current_user_url = f'{self.gateway_base_url}/api/users/me/'
        self.gateway_current_user_image_url = f'{self.gateway_base_url}/api/images/me/'
        self.token = None

    def login(self, data):
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

    def get_current_user(self):
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
    
    def get_current_user_image(self):
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