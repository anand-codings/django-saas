"""Plan/tier definitions, feature entitlements, and usage quotas."""

from django.db import models
from shared.models.base import BaseModel
from shared.types.enums import Currency, Status


class Plan(BaseModel):
    """A subscription plan/tier (e.g., Free, Starter, Pro, Enterprise)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)

    # Provider mapping
    stripe_monthly_price_id = models.CharField(max_length=255, blank=True, default="")
    stripe_yearly_price_id = models.CharField(max_length=255, blank=True, default="")

    # Limits
    max_members = models.IntegerField(default=1, help_text="Max team members. 0 = unlimited.")
    max_storage_mb = models.IntegerField(default=100, help_text="Max storage in MB. 0 = unlimited.")
    max_api_calls_per_month = models.IntegerField(default=1000, help_text="0 = unlimited.")

    # Display
    is_public = models.BooleanField(default=True, help_text="Show on pricing page")
    sort_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Highlight on pricing page")
    trial_days = models.IntegerField(default=0)

    class Meta(BaseModel.Meta):
        ordering = ["sort_order", "price_monthly"]

    def __str__(self):
        return self.name

    @classmethod
    def from_stripe_price(cls, price_id):
        """Resolve a Plan from a Stripe price ID, or None."""
        from django.db.models import Q

        return cls.objects.filter(
            Q(stripe_monthly_price_id=price_id) | Q(stripe_yearly_price_id=price_id)
        ).first()


class PlanFeature(BaseModel):
    """A feature or entitlement included in a plan."""

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="features")
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True, default="")

    # Feature type
    is_boolean = models.BooleanField(default=True, help_text="True = on/off feature, False = metered/limited")
    limit_value = models.IntegerField(null=True, blank=True, help_text="Numeric limit for metered features")
    limit_unit = models.CharField(max_length=50, blank=True, default="", help_text="e.g., 'requests', 'GB', 'users'")

    class Meta(BaseModel.Meta):
        ordering = ["plan", "name"]
        constraints = [
            models.UniqueConstraint(fields=["plan", "slug"], name="unique_plan_feature_slug"),
        ]

    def __str__(self):
        if self.is_boolean:
            return f"{self.plan.name}: {self.name}"
        return f"{self.plan.name}: {self.name} ({self.limit_value} {self.limit_unit})"


class PlanFeatureDefinition(BaseModel):
    """Global feature definition — the master list of all possible features.

    PlanFeature instances reference these to maintain consistency across plans.
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=100, blank=True, default="")

    class Meta(BaseModel.Meta):
        ordering = ["category", "name"]

    def __str__(self):
        return self.name
