from django.apps import AppConfig


class DataPortabilityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.data_portability"
    label = "data_portability"
    verbose_name = "User data export ('Download my data') and account deletion (right to be forgotten)"
