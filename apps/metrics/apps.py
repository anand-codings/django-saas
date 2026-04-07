from django.apps import AppConfig


class MetricsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.metrics"
    label = "metrics"
    verbose_name = "Business metrics: MRR, churn, DAU/MAU, conversion funnels, cohort analysis"
