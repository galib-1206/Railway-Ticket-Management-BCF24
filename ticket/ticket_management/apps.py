from django.apps import AppConfig
from .listener import start_redis_listener

class TicketManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticket_management'

    def ready(self):
        start_redis_listener()
