from django.apps import AppConfig


class StaffPermissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.staff_permissions"
    label = "staff_permissions"
    verbose_name = "Staff-specific RBAC: support vs engineering vs finance access levels"
