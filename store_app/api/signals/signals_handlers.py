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


def get_user_data(user_email):
    try:
        logger.info(f"Getting user data with email {user_email}")
        data = {"email":settings.STORE_USERNAME,"password": settings.STORE_PASSWORD}
        gateway = Gateway()
        token,error = gateway.login(data)
        
        if error:
            logger.error(f"Failed to login to gateway: {error}")
            return None, None, None

        customer_user = gateway.get_user_by_email(user_email)
        customer_user_image = gateway.get_user_image_by_email(user_email)
        customer_user_image = customer_user_image.get('filename', None) if customer_user_image else None
        
        logger.info(f"Customer user: {customer_user}")
        logger.info(f"Customer user image: {customer_user_image}")
        
        return token, customer_user, customer_user_image
    
    except Exception as e:
        logger.error(f"Error getting user data: {e}")
        return None, None, None


def send_notification(token, user, user_image, notification_data):
    try:
        notification = Notification()
        notification.token = token
        

        notification_payload = {
            "message": notification_data.get('message', None),
            "sender": user.get('email', None),
            "title": notification_data.get('title', None),
            "userId": user.get('id', None),
            "username": notification_data.get('username', None),
            "userEmail": notification_data.get('userEmail', None),
            "userImage": user_image,
            "externalArgs": json.dumps({"sender_name" : user.get('username', None)})
        }
        created_notification = notification.add_user_notification(payload=notification_payload)
        logger.info(f"Notification created: {created_notification}")
        return created_notification
    except Exception as error:
        logger.error(f"Failed to post notification : {error}")
        return None


@receiver(post_save, sender=Order)
def send_notification_to_admin_when_order_is_submitted(sender, instance, created, **kwargs):
    try:
        # Order created signal
        if created:
            logger.info(f"Order Created. Triggering notification for admin...")

			# Get user and token
            order_customer_email = instance.customer_email
            token, customer_user, customer_user_image = get_user_data(user_email=order_customer_email)

			# Add Notification
            if customer_user and token:
                logger.info(f"Posting notification to admin...")
                notification_data = {
                    "message": f"Customer {customer_user.get('username', None)} has submitted a new order.",
                    "title": f"New Order Submitted",
                    "username": "admin",
                    "userEmail": "admin@domain.com",
                }
                
                created_notification = send_notification(
                    token=token, 
                    user=customer_user, 
                    user_image=customer_user_image, 
                    notification_data=notification_data
                    )

                if created_notification:
                    notification_sender = created_notification.get('sender', None)
                    notification_receiver = created_notification.get('userEmail', None)
                    if notification_sender != notification_receiver and notification_receiver == "admin@domain.com":
                        logger.info("Notification receiver signal triggered...")
                        channel_layer = get_channel_layer()
                        groupe_name = f"user-{created_notification.get('username', None)}-websocket-notifications"
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
            
            # Get user and token
            admin_email = "admin@domain.com"
            token, user, user_image = get_user_data(user_email=admin_email)
            
            # Add Notification
            if user and token:
                order_payment_status = { "P": "Pending", "C": "Complete", "F": "Failed" }
                notification_data = {
                    "message": f"Your Order is updated to {order_payment_status[instance.payment_status]}.",
                    "title": f"Order Updated",
                    "username": instance.customer_name,
                    "userEmail": instance.customer_email
                }
                
                created_notification = send_notification(
                    token=token, 
                    user=user, 
                    user_image=user_image, 
                    notification_data=notification_data
                    )

                if created_notification:
                    notification_sender = created_notification.get('sender', None)
                    notification_receiver = created_notification.get('userEmail', None)
                    if notification_sender != notification_receiver and notification_sender == "admin@domain.com":
                        logger.info("Notification receiver signal triggered...")
                        channel_layer = get_channel_layer()
                        groupe_name = f"user-{created_notification.get('username', None)}-websocket-notifications"
                        event = {
                            "type": "order_submitted_notification",
                            "text": created_notification,
                        }

                        async_to_sync(channel_layer.group_send)(groupe_name, event)
                    else:
                        logger.info(f"Notification sender {notification_sender} and receiver {notification_receiver} are the same. Notification receiver signal not triggered...")


    except Exception as e:
        logger.error(f"Error adding notification receiver signal: {e}")








