from django.apps import AppConfig


class I18NConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.i18n"
    label = "i18n"
    verbose_name = "Translation management with admin UI for translators and dynamic content translation"
