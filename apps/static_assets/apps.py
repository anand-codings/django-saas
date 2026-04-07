from django.apps import AppConfig


class StaticAssetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.static_assets"
    label = "static_assets"
    verbose_name = "Static file pipeline: collection, compression, hashing, CDN upload"
