from django.apps import AppConfig


class UsageMeteringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.usage_metering"
    label = "usage_metering"
    verbose_name = "Track metered billing events: API calls, storage consumed, seats used"
