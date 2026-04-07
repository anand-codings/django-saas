from django.apps import AppConfig


class SupportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.support"
    label = "support"
    verbose_name = "Customer support ticket system: create/reply/resolve, SLA tracking, assignment"
