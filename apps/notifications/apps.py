from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    label = "app_notifications"
    verbose_name = "Unified notification system: in-app, email digest, push, SMS, Slack with per-user preferences"
