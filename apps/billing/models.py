"""Subscription management, payment processing, and invoicing with provider abstraction."""

from django.conf import settings
from django.db import models

from shared.models.base import BaseModel, TenantAwareModel
from shared.providers.payment import PaymentStatus, SubscriptionStatus
from shared.types.enums import Currency, Interval


class BillingCustomer(BaseModel):
    """Maps a user/org to a payment provider customer."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="billing_customer",
    )
    organization_id = models.UUIDField(null=True, blank=True, db_index=True)

    # Provider
    stripe_customer_id = models.CharField(max_length=255, unique=True, blank=True, default="")
    provider = models.CharField(max_length=50, default="stripe")

    # Info
    email = models.EmailField(blank=True, default="")
    name = models.CharField(max_length=255, blank=True, default="")
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    tax_id = models.CharField(max_length=50, blank=True, default="")

    class Meta(BaseModel.Meta):
        verbose_name = "billing customer"

    def __str__(self):
        return f"{self.email or self.name} ({self.provider})"


class Subscription(BaseModel):
    """A subscription linking a customer to a plan."""

    customer = models.ForeignKey(BillingCustomer, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey("plans.Plan", on_delete=models.PROTECT, related_name="subscriptions")

    # Status
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in SubscriptionStatus],
        default=SubscriptionStatus.ACTIVE.value,
    )

    # Billing interval
    interval = models.CharField(max_length=20, choices=Interval.choices, default=Interval.MONTHLY)

    # Dates
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)

    # Provider
    stripe_subscription_id = models.CharField(max_length=255, unique=True, blank=True, default="")

    # Quantity (for per-seat billing)
    quantity = models.IntegerField(default=1)

    class Meta(BaseModel.Meta):
        verbose_name = "subscription"

    def __str__(self):
        return f"{self.customer} → {self.plan} ({self.status})"

    @property
    def is_active(self):
        return self.status in (SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value)


class Invoice(BaseModel):
    """An invoice generated for a subscription or one-time charge."""

    customer = models.ForeignKey(BillingCustomer, on_delete=models.CASCADE, related_name="invoices")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")

    # Amounts (in smallest currency unit, e.g., cents)
    amount_due = models.IntegerField(default=0)
    amount_paid = models.IntegerField(default=0)
    amount_remaining = models.IntegerField(default=0)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in PaymentStatus],
        default=PaymentStatus.PENDING.value,
    )

    # Dates
    due_date = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Provider
    stripe_invoice_id = models.CharField(max_length=255, unique=True, blank=True, default="")
    invoice_pdf_url = models.URLField(blank=True, default="")

    # Line items stored as JSON for flexibility
    line_items = models.JSONField(default=list, blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = "invoice"

    def __str__(self):
        return f"Invoice {self.id} — {self.customer} — {self.status}"


class PaymentMethod(BaseModel):
    """A stored payment method for a customer."""

    customer = models.ForeignKey(BillingCustomer, on_delete=models.CASCADE, related_name="payment_methods")

    # Provider
    stripe_payment_method_id = models.CharField(max_length=255, unique=True, blank=True, default="")
    provider = models.CharField(max_length=50, default="stripe")

    # Card info (for display only — never store full card numbers)
    card_brand = models.CharField(max_length=20, blank=True, default="")  # visa, mastercard, etc.
    card_last4 = models.CharField(max_length=4, blank=True, default="")
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)

    is_default = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        verbose_name = "payment method"

    def __str__(self):
        return f"{self.card_brand} •••• {self.card_last4}"


class UsageRecord(BaseModel):
    """Tracks metered usage for usage-based billing."""

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="usage_records")
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
