from django.apps import AppConfig


class ExportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.exports"
    label = "exports"
    verbose_name = "Async data export: CSV/Excel/PDF generation in background with download links"
