from django.apps import AppConfig


class AuditLogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit_log"
    label = "audit_log"
    verbose_name = "Immutable audit trail: who changed what, when, from where, with before/after diffs"
