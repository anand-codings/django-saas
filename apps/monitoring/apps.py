from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.monitoring"
    label = "monitoring"
    verbose_name = "APM integration: Sentry, Prometheus metrics, structured logging, OpenTelemetry"
