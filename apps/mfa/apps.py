from django.apps import AppConfig


class MfaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mfa"
    label = "app_mfa"
    verbose_name = "Multi-factor authentication: TOTP, SMS codes, WebAuthn/passkeys, and backup codes"
