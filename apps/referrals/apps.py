from django.apps import AppConfig


class ReferralsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.referrals"
    label = "referrals"
    verbose_name = "Referral/affiliate program: unique links, reward tracking, fraud detection"
