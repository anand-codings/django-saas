from django.apps import AppConfig


class InternalToolsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.internal_tools"
    label = "internal_tools"
    verbose_name = "Internal support/ops views: user lookup, subscription management, manual actions"
