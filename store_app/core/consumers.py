from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.template.loader import get_template
from store_app.tools.helpers import *

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        try:
            logger.info("Connecting to websocket")
            logger.info(self.channel_name)
            self.GROUP_NAME = 'user-notifications'
            self.user = self.scope['user']
            logger.info(f"NotificationConsumer Scope user {self.user}")
            
            # if not self.user.is_authenticated:
            #     self.close()
            #     return
            async_to_sync(self.channel_layer.group_add)(
                self.GROUP_NAME, self.channel_name
            )
            self.accept()
            logger.info("Connected to websocket")
        except Exception as e:
            logger.error(f"NotificationConsumer connect Error: {e}")

    def disconnect(self, close_code):
        try:
            logger.info("Disconnected from websocket")
            async_to_sync(self.channel_layer.group_discard)(
                self.GROUP_NAME, self.channel_name
            )
        except Exception as e:
            logger.error(f"NotificationConsumer disconnect Error: {e}")
        
        # if self.user.is_authenticated:
        #     async_to_sync(self.channel_layer.group_discard)(
        #         self.GROUP_NAME, self.channel_name
        #     )

    def notification_created(self, event):
        try:
            logger.info("Sending notification to websocket client...")
            html = get_template("partials/navbar_notifications.html").render(
                context={"notification": event["text"]}
            )
            # logger.info(f"html is : {html}")
            self.send(text_data=html)
            logger.info("Notification sent to websocket client...")
        except Exception as e:
            logger.error(f"NotificationConsumer notification_created Error: {e}")
        
    # def user_joined(self, event):
    #     html = get_template("core/partials/notification.html").render(
    #         context={"username": event["text"]}
    #     )
    #     self.send(text_data=html)