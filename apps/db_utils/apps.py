from django.apps import AppConfig


class DbUtilsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.db_utils"
    label = "db_utils"
    verbose_name = "Database utilities: migration safety, read replica routing, connection pooling"
