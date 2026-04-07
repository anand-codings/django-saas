from django.apps import AppConfig


class WebhooksInboundConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.webhooks_inbound"
    label = "webhooks_inbound"
    verbose_name = "Inbound webhook receiver: accept and verify webhooks from external services"
