from django.apps import AppConfig


class ZapierConnectorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.zapier_connector"
    label = "zapier_connector"
    verbose_name = "Zapier/Make/n8n integration layer: triggers, actions, searches REST API"
