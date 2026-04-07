from django.apps import AppConfig


class WaitlistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.waitlist"
    label = "waitlist"
    verbose_name = "Pre-launch waitlist: email collection, position tracking, referral queue jumping"
