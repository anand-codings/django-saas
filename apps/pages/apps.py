from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    label = "pages"
    verbose_name = "Static/marketing pages CMS with WYSIWYG editing and slug management"
