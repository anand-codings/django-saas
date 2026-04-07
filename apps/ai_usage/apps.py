from django.apps import AppConfig


class AiUsageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai_usage"
    label = "ai_usage"
    verbose_name = "AI cost tracking: token counts, cost per request, per-tenant budgets, usage dashboards"
