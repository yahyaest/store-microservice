import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.template.loader import get_template
from store_app.tools.helpers import *
from urllib.parse import parse_qs

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        try:
            logger.info("Client try connecting to websocket")
            logger.info(self.channel_name)
            self.user = self.scope.get('user', None)
            
            if not self.user:
                self.close()
                return
            
            self.GROUP_NAME = f"user-{self.user.get('username', '').replace('@', '_AT_')}-websocket-notifications"
            logger.info(f"Websocket NotificationConsumer Scope user {self.user}")
            
            query_params = parse_qs(self.scope['query_string'].decode('utf-8'))            
            logger.debug(f"query_params: {query_params}")

                
            # if not self.user.is_authenticated:
            #     self.close()
            #     return
            async_to_sync(self.channel_layer.group_add)(
                self.GROUP_NAME, self.channel_name
            )
            self.accept()
            logger.info("Client connected to websocket")
        except Exception as e:
            logger.error(f"Websocket NotificationConsumer connect Error: {e}")

    def disconnect(self, close_code):
        try:
            logger.info("Client disconnected from websocket")
            async_to_sync(self.channel_layer.group_discard)(
                self.GROUP_NAME, self.channel_name
            )
        except Exception as e:
            logger.error(f"Websocket NotificationConsumer disconnect Error: {e}")
        
        # if self.user.is_authenticated:
        #     async_to_sync(self.channel_layer.group_discard)(
        #         self.GROUP_NAME, self.channel_name
        #     )

    def order_submitted_notification(self, event):
        try:
            logger.info("Sending notification to websocket client...")
            logger.info(f"event text is : {event['text']}")
            data = json.dumps(event['text'])
            self.send(text_data=data)

        except Exception as e:
            logger.error(f"Websocket NotificationConsumer notification_created Error: {e}")