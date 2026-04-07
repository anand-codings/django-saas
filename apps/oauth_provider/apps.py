from django.apps import AppConfig


class OauthProviderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.oauth_provider"
    label = "oauth_provider"
    verbose_name = "OAuth2 provider: let third-party apps authenticate against your platform"
