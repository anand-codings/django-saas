from django.apps import AppConfig


class ScheduledJobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.scheduled_jobs"
    label = "scheduled_jobs"
    verbose_name = "Database-driven periodic job management with admin UI and execution history"
