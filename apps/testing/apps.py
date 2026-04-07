from django.apps import AppConfig


class TestingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.testing"
    label = "testing"
    verbose_name = "Shared test infrastructure: factories, assertion mixins, API test helpers, tenant-aware base classes"
