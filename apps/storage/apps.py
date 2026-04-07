from django.apps import AppConfig


class StorageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.storage"
    label = "storage"
    verbose_name = "Cloud-agnostic file storage abstraction (S3, GCS, Azure, local) with signed URLs and CDN"
