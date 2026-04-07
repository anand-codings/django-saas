from django.apps import AppConfig


class SsoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sso"
    label = "sso"
    verbose_name = "SAML/OIDC single sign-on for enterprise B2B customers"
