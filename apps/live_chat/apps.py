from django.apps import AppConfig


class LiveChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.live_chat"
    label = "live_chat"
    verbose_name = "Real-time customer-to-support chat via WebSockets"
