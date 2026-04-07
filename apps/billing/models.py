"""Subscription management, payment processing, and invoicing via dj-stripe.

BillingCustomer is the thin linking layer between users/orgs and dj-stripe.
Subscription, Invoice, and PaymentMethod are handled by dj-stripe models directly.
"""

from django.conf import settings
from django.db import models
from shared.models.base import BaseModel


class BillingCustomer(BaseModel):
    """Links a user or organization to a dj-stripe Customer."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="billing_customer",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="billing_customer",
    )
    djstripe_customer = models.OneToOneField(
        "djstripe.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_customer",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "billing customer"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, organization__isnull=True)
                    | models.Q(user__isnull=True, organization__isnull=False)
                ),
                name="billing_customer_user_xor_org",
            ),
        ]

    def __str__(self):
        if self.user:
            return f"BillingCustomer for user {self.user}"
        return f"BillingCustomer for org {self.organization}"

    @property
    def subscriber_email(self):
        if self.user:
            return self.user.email
        if self.organization and self.organization.owner:
            return self.organization.owner.email
        return ""

    @property
    def subscriber_name(self):
        if self.user:
            return self.user.get_full_name()
        if self.organization:
            return self.organization.name
        return ""


class UsageRecord(BaseModel):
    """Tracks metered usage for usage-based billing."""

    subscription = models.ForeignKey(
        "djstripe.Subscription",
        on_delete=models.CASCADE,
        related_name="usage_records",
    )
    feature_slug = models.SlugField(help_text="Which metered feature this usage is for")

    quantity = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Optional metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = "usage record"
        indexes = [
            models.Index(fields=["subscription", "feature_slug", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.feature_slug}: {self.quantity} @ {self.timestamp}"
