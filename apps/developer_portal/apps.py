from django.apps import AppConfig


class DeveloperPortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.developer_portal"
    label = "developer_portal"
    verbose_name = "Public developer portal: API reference, SDKs, code samples, sandbox"
