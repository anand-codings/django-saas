from django.apps import AppConfig


class AnnouncementsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.announcements"
    label = "announcements"
    verbose_name = "In-app announcements, changelogs, 'what's new' banners, maintenance notices"
