from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    label = "api"
    verbose_name = "Core API configuration for both DRF and Django Ninja: versioning, auth, pagination, routing"
