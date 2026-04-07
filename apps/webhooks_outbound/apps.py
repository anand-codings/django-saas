from django.apps import AppConfig


class WebhooksOutboundConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.webhooks_outbound"
    label = "webhooks_outbound"
    verbose_name = "Outbound webhook system: registration, HMAC signing, retries, delivery logs"
