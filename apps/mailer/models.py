"""Transactional email sending with provider abstraction (SES, Resend, SendGrid, Postmark)."""

from django.conf import settings
from django.db import models

from shared.models.base import BaseModel


class EmailTemplate(BaseModel):
    """A managed email template with variable substitution."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    subject = models.CharField(max_length=255)
    body_text = models.TextField(blank=True, default="")
    body_html = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="", help_text="Internal notes about when this template is used")

    # Versioning
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    # Categories
    category = models.CharField(max_length=50, blank=True, default="", help_text="e.g., auth, billing, marketing")

    class Meta(BaseModel.Meta):
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} (v{self.version})"


class EmailLog(BaseModel):
    """Log of every email sent through the system."""

    # Recipient
    to_email = models.EmailField(db_index=True)
    from_email = models.EmailField()

    # Content
    subject = models.CharField(max_length=255)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs")

    # Delivery
    provider = models.CharField(max_length=50, help_text="e.g., ses, sendgrid, postmark")
    message_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("queued", "Queued"),
            ("sent", "Sent"),
            ("delivered", "Delivered"),
            ("bounced", "Bounced"),
            ("failed", "Failed"),
            ("complained", "Complained"),
        ],
        default="queued",
    )
    error = models.TextField(blank=True, default="")

    # Tracking
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    # Context
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="email_logs")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = "email log"
        indexes = [
            models.Index(fields=["to_email", "status"]),
            models.Index(fields=["provider", "status", "created_at"]),
        ]

    def __str__(self):
        return f"Email to {self.to_email}: {self.subject} ({self.status})"
