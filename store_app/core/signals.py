from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from store_app.tools.helpers import logger
from store_app.core.models import WebsocketSignalTrigger


# Define a signal
notification_signal = Signal()


@receiver(post_save, sender=WebsocketSignalTrigger)
def add_notification_receiver_signal_with_post_save(sender, **kwargs):
    try:
        logger.info(f"kwargs: {kwargs}")
        socket_data = kwargs['instance'].socket_data
        if socket_data:
            notification = socket_data['notification']
            notification_sender = socket_data['notification_sender']
            notification_receiver = socket_data['notification_receiver']
            if notification_sender != notification_receiver:
                logger.info("Notification receiver signal triggered...")
                channel_layer = get_channel_layer()
                groupe_name = 'user-notifications'
                event = {
                    "type": "notification_created",
                    "text": notification
                }
                async_to_sync(channel_layer.group_send)(groupe_name, event)
        else:
            logger.warning("No socket data provided. Notification receiver signal not triggered...")
    except Exception as e:
        logger.error(f"Error adding notification receiver signal: {e}")


@receiver(notification_signal)
def add_notification_receiver_signal(sender, **kwargs):
    try:
        notification = kwargs['notification']
        notification_sender = kwargs['notification_sender']
        notification_receiver = kwargs['notification_receiver']
        if notification_sender != notification_receiver:
            logger.info("Notification receiver signal triggered...")
            channel_layer = get_channel_layer()
            groupe_name = 'user-notifications'
            event = {
                "type": "notification_created",
                "text": notification,
            }
            async_to_sync(channel_layer.group_send)(groupe_name, event)
        else:
            logger.info(f"Notification sender {notification_sender} and receiver {notification_receiver} are the same. Notification receiver signal not triggered...")
    except Exception as e:
        logger.error(f"Error adding notification receiver signal: {e}")
