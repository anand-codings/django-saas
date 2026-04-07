from django.apps import AppConfig


class EmailTrackingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.email_tracking"
    label = "email_tracking"
    verbose_name = "Email open/click tracking, bounce/complaint handling via ESP webhooks"
