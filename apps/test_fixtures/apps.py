from django.apps import AppConfig


class TestFixturesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.test_fixtures"
    label = "test_fixtures"
    verbose_name = "Seed data generation: demo accounts, sample content, realistic fake data"
