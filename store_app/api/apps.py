from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store_app.api'

    def ready(self):
        from .signals import signals_handlers