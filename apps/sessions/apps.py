from django.apps import AppConfig


class SessionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sessions"
    label = "app_sessions"
    verbose_name = "Enhanced session management: device listing, 'log out all', activity tracking"
