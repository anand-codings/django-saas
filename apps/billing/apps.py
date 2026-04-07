from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.billing"
    label = "billing"
    verbose_name = "Subscription management, payment processing, and invoicing with provider abstraction"

    def ready(self):
        import apps.billing.webhooks  # noqa: F401 — registers dj-stripe signal handlers
