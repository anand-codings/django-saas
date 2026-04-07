from django.apps import AppConfig


class SandboxConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sandbox"
    label = "sandbox"
    verbose_name = "Test/sandbox mode: separate data environments, test API keys, fake payments"
