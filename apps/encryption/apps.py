from django.apps import AppConfig


class EncryptionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.encryption"
    label = "encryption"
    verbose_name = "Field-level encryption for PII and sensitive data with KMS abstraction"
