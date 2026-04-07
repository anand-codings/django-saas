from django.apps import AppConfig


class PushNotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.push_notifications"
    label = "app_push_notifications"
    verbose_name = "Web push (VAPID/FCM) and mobile push (APNs/FCM) registration and delivery"
