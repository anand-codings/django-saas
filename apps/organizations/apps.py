from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.organizations"
    label = "organizations"
    verbose_name = "Organization/workspace/team model with membership, roles, and org-level settings"

    def ready(self):
        import apps.organizations.signals  # noqa: F401
