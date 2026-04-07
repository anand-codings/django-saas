from django.apps import AppConfig


class ImpersonationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.impersonation"
    label = "impersonation"
    verbose_name = "Admin 'log in as user' capability with full audit trail"
