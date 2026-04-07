from django.apps import AppConfig


class RateLimitingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rate_limiting"
    label = "rate_limiting"
    verbose_name = "Per-user/org/key/IP throttling with plan-tier limits and Redis sliding window"
