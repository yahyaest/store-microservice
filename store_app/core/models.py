from django.db import models

# Create your models here.

class WebsocketSignalTrigger(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    socket_data = models.JSONField(blank=True, null=True)