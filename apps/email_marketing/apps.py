from django.apps import AppConfig


class EmailMarketingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.email_marketing"
    label = "email_marketing"
    verbose_name = "Marketing email: subscriber lists, campaigns, drip sequences, unsubscribe management"
