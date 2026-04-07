from django.apps import AppConfig


class ActivityStreamConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.activity_stream"
    label = "activity_stream"
    verbose_name = "User-facing activity feed: social-style timeline for orgs and users"
