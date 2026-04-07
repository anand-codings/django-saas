from django.apps import AppConfig


class UserPreferencesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.user_preferences"
    label = "user_preferences"
    verbose_name = "User-level settings: notification preferences, theme, default dashboard"
