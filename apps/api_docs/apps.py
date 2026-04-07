from django.apps import AppConfig


class ApiDocsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api_docs"
    label = "api_docs"
    verbose_name = "Auto-generated OpenAPI/Swagger documentation for both DRF and Ninja endpoints"
