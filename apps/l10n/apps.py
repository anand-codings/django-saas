from django.apps import AppConfig


class L10NConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.l10n"
    label = "l10n"
    verbose_name = "Localization: timezone-aware display, currency formatting, date/number formats"
