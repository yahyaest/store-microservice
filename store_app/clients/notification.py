import requests
from store_app import settings
from store_app.clients.gateway import Gateway
from store_app.tools.helpers import *


class Notification:
    def __init__(self) -> None:
        self.notification_base_url = settings.NOTIFICATION_BASE_URL
        self.notification_url = f'{self.notification_base_url}/api/notifications'
        self.bulk_notification_url = f'{self.notification_base_url}/api/bulk_notifications'
        self.token = None

    def add_user_notification(self, payload):
        try:
            if not self.token:
                raise ValueError("No token was provided. Failed to post notification")

            headers = {}
            headers['Content-Type'] = 'application/json'
            headers['Authorization'] = f'Bearer {self.token}'

            response = requests.post(url=self.notification_url, verify=False, json=payload, headers=headers)
            if response.status_code == 201:
                notification = response.json()
                return notification
            else:
                logger.error("=====> add notification failed --> failed")
                logger.error(response.status_code)
                logger.error(response.text)
            return None
        except Exception as error:
            logger.error(f"Failed to create notification: {error}")

    def add_product_owner_notification(self, app_signin_payload, product_owner, data):
        try:
            gateway = Gateway()
            product_owner_user = gateway.get_user_by_email(email=product_owner, use_admin_token=True, admin_credentials=app_signin_payload)
            if not gateway.token:
                raise ValueError("No token was provided. Failed to post notification")

            headers = {}
            headers['Content-Type'] = 'application/json'
            headers['Authorization'] = f'Bearer {gateway.token}'

            payload = {
                "userEmail": product_owner_user["email"],
                "username": product_owner_user["username"],
                "userImage": data["userImage"],
                "userId": product_owner_user["id"],
                "title": data["title"],
                "message": data["message"],
                "seen": False,
            }

            response = requests.post(url=self.notification_url, verify=False, json=payload, headers=headers)
            if response.status_code == 201:
                notification = response.json()
                return notification
            else:
                logger.error("=====> add notification failed --> failed")
                logger.error(response.status_code)
                logger.error(response.text)
            return None

        except Exception as error:
            logger.error(f"Failed to create notification: {error}")

    def get_user_notifications(self,email):
        try:
            notification_url = f"{self.notification_base_url}/api/notifications/?userEmail={email}"
            if not self.token:
                raise ValueError("No token was provided. Failed to post notification")

            headers = {}
            headers['Content-Type'] = 'application/json'
            headers['Authorization'] = f'Bearer {self.token}'

            response = requests.get(url=notification_url, verify=False, headers=headers)
            if response.status_code == 200:
                notification = response.json()
                return notification
            else:
                logger.error("=====> get user notifications failed --> failed")
                logger.error(response.status_code)
                logger.error(response.text)
            return None

        except Exception as error:
            logger.error(f"Failed to get notifications: {error}")

    def update_notification(self, notification_id, payload):
        try:
            if not self.token:
                raise ValueError("No token was provided. Failed to post notification")

            headers = {}
            headers['Content-Type'] = 'application/json'
            headers['Authorization'] = f'Bearer {self.token}'

            response = requests.patch(url=f"{self.notification_url}/{notification_id}", verify=False, json=payload, headers=headers)
            if response.status_code == 200:
                notification = response.json()
                return notification
            else:
                logger.error("=====> update notification failed --> failed")
                logger.error(response.status_code)
                logger.error(response.text)
            return None

        except Exception as error:
            logger.error(f"Failed to update notification: {error}")

    def update_bulk_notification(self, payload):
        try:
            if not self.token:
                raise ValueError("No token was provided. Failed to post notification")

            headers = {}
            headers['Content-Type'] = 'application/json'
            headers['Authorization'] = f'Bearer {self.token}'

            response = requests.patch(url=self.bulk_notification_url, verify=False, json=payload, headers=headers)
            if response.status_code == 200:
                notifications = response.json()
                return notifications
            else:
                logger.error("=====> update notifications failed --> failed")
                logger.error(response.status_code)
                logger.error(response.text)
            return None

        except Exception as error:
            logger.error(f"Failed to update notifications: {error}")

    def delete_notification(self, notification_id):
        try:
            if not self.token:
                raise ValueError("No token was provided. Failed to post notification")

            headers = {}
            headers['Content-Type'] = 'application/json'
            headers['Authorization'] = f'Bearer {self.token}'

            response = requests.delete(url=f"{self.notification_url}/{notification_id}", verify=False, headers=headers)
            if response.status_code == 204:
                notification = response.json()
                return notification
            else:
                logger.error("=====> dlete notification failed --> failed")
                logger.error(response.status_code)
                logger.error(response.text)
            return None

        except Exception as error:
            logger.error(f"Failed to delete notification: {error}")