from django.apps import AppConfig


class AdminDashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.admin_dashboard"
    label = "admin_dashboard"
    verbose_name = "Enhanced Django admin with custom dashboards, charts, and quick actions"
