from django.apps import AppConfig


class CachingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.caching"
    label = "caching"
    verbose_name = "Redis/Memcached caching with tenant-scoped keys and invalidation helpers"
