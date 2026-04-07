from django.apps import AppConfig


class InvitationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.invitations"
    label = "app_invitations"
    verbose_name = "Email invite tokens for platform or organization, with expiry and tracking"
