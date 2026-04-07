"""Unified notification system: in-app, email digest, push, SMS, Slack with per-user preferences."""

from django.conf import settings
from django.db import models

from shared.models.base import BaseModel
from shared.providers.notification import NotificationChannel, NotificationPriority


class NotificationType(BaseModel):
    """Definition of a notification type (e.g., 'invoice.paid', 'member.invited')."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="e.g., invoice.paid, member.invited")
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="", help_text="e.g., billing, team, system")

    # Default channels for this notification type
    default_channels = models.JSONField(
        default=list,
        help_text='e.g., ["in_app", "email"]',
    )

    # Template
    title_template = models.CharField(max_length=255, help_text="Supports {variable} substitution")
    body_template = models.TextField(help_text="Supports {variable} substitution")

    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        ordering = ["category", "name"]

    def __str__(self):
        return self.slug


class Notification(BaseModel):
    """A notification instance sent to a specific user."""

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name="instances")

    # Content (rendered from template + data)
    title = models.CharField(max_length=255)
    body = models.TextField()
    action_url = models.URLField(blank=True, default="")
    data = models.JSONField(default=dict, blank=True, help_text="Arbitrary payload for the notification")

    # Delivery
    channels_sent = models.JSONField(default=list, help_text="Which channels were used")
    priority = models.CharField(
        max_length=20,
        choices=[(p.value, p.value) for p in NotificationPriority],
        default=NotificationPriority.NORMAL.value,
    )

    # Status
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # Actor (who triggered this notification)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="triggered_notifications",
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.notification_type.slug}] {self.title} → {self.recipient}"

    def mark_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at"])


class NotificationPreference(BaseModel):
    """Per-user, per-notification-type channel preferences.

    Allows users to opt in/out of specific channels for specific notification types.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences")
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name="preferences")

    # Which channels the user wants for this notification type
    channels = models.JSONField(
        default=list,
        help_text='e.g., ["in_app", "email", "push"]',
    )
    is_muted = models.BooleanField(default=False, help_text="Completely silence this notification type")

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=["user", "notification_type"], name="unique_user_notification_pref"),
        ]

    def __str__(self):
        return f"{self.user} → {self.notification_type.slug}: {self.channels}"
