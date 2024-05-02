import json
from django.conf import settings
from django.dispatch import Signal, receiver
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from store_app.api.models import Order
from store_app.tools.helpers import logger
from store_app.clients.gateway import Gateway
from store_app.clients.notification import Notification

order_created = Signal()

@receiver(order_created)
def on_order_created(sender, **kwargs):
	logger.info(kwargs['order'])


# ... your serializer and view logic

@receiver(post_save, sender=Order)
def send_notification_to_admin_when_order_is_submitted(sender, instance, created, **kwargs):
    try:
        # Order created signal
        if created:
            logger.info(f"Order Created. Triggering notification for admin...")

			# Get user and token
            data = {"email":settings.STORE_USERNAME,"password": settings.STORE_PASSWORD}
            gateway = Gateway()
            token,error = gateway.login(data)
            
            logger.info(f"Connected to gateway. Posting notification...")
            order_customer_email = instance.customer_email
            
            customer_user = gateway.get_user_by_email(order_customer_email)
            customer_user_image = gateway.get_user_image_by_email(order_customer_email)
            customer_user_image = customer_user_image.get('filename', None) if customer_user_image else None
            
            logger.info(f"Customer user: {customer_user}")
            logger.info(f"Customer user image: {customer_user_image}")
            

			# Add Notification
            if customer_user and token:
                try:
                    logger.info(f"Posting notification to admin...")
                    notification = Notification()
                    notification.token = token
                    

                    notification_payload = {
						"message": f"Customer {customer_user.get('username', None)} has submitted a new order.",
						"sender": customer_user.get('email', None),
						"title": f"New Order Submitted",
						"userId": customer_user.get('id', None),
						"username": "admin",
						"userEmail": "admin@domain.com",
						"userImage": customer_user_image,
						"externalArgs": json.dumps({"sender_name" : customer_user.get('username', None)})
					}
                    created_notification = notification.add_user_notification(payload=notification_payload)
                    logger.info(f"Notification created: {created_notification}")
                except Exception as error:
                    logger.error(f"Failed to post notification : {error}")


                notification_sender = created_notification.get('sender', None)
                notification_receiver = created_notification.get('userEmail', None)
                if notification_sender != notification_receiver and notification_receiver == "admin@domain.com":
                    logger.info("Notification receiver signal triggered...")
                    channel_layer = get_channel_layer()
                    groupe_name = 'user-websocket-notifications'
                    event = {
                        "type": "order_submitted_notification",
                        "text": created_notification,
					}

                    async_to_sync(channel_layer.group_send)(groupe_name, event)
                else:
                    logger.info(f"Notification sender {notification_sender} and receiver {notification_receiver} are the same. Notification receiver signal not triggered...")

		# Order updated signal
        else:
            logger.info(f"Order updated. Triggering notification...")

    except Exception as e:
        logger.error(f"Error adding notification receiver signal: {e}")








