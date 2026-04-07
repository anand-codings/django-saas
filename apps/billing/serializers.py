from rest_framework import serializers

from apps.billing.models import BillingCustomer, UsageRecord


class BillingCustomerSerializer(serializers.ModelSerializer):
    has_active_subscription = serializers.SerializerMethodField()

    class Meta:
        model = BillingCustomer
        fields = ["id", "user", "organization", "djstripe_customer", "has_active_subscription", "created_at"]
        read_only_fields = fields

    def get_has_active_subscription(self, obj):
        if not obj.djstripe_customer:
            return False
        return obj.djstripe_customer.subscriptions.filter(
            status__in=["active", "trialing"],
        ).exists()


class SubscriptionSerializer(serializers.Serializer):
    """Read-only serializer for dj-stripe Subscription objects."""

    id = serializers.CharField()
    status = serializers.CharField()
    current_period_start = serializers.DateTimeField()
    current_period_end = serializers.DateTimeField()
    cancel_at_period_end = serializers.BooleanField()
    canceled_at = serializers.DateTimeField()
    trial_start = serializers.DateTimeField()
    trial_end = serializers.DateTimeField()
    created = serializers.DateTimeField()
    plan_id = serializers.SerializerMethodField()
    plan_name = serializers.SerializerMethodField()
    plan_amount = serializers.SerializerMethodField()
    plan_interval = serializers.SerializerMethodField()

    def get_plan_id(self, obj):
        return obj.plan.id if obj.plan else None

    def get_plan_name(self, obj):
        if obj.plan and obj.plan.product:
            return obj.plan.product.name
        return None

    def get_plan_amount(self, obj):
        return obj.plan.amount if obj.plan else None

    def get_plan_interval(self, obj):
        return obj.plan.interval if obj.plan else None


class SubscriptionCancelSerializer(serializers.Serializer):
    at_period_end = serializers.BooleanField(default=True)


class InvoiceSerializer(serializers.Serializer):
    """Read-only serializer for dj-stripe Invoice objects."""

    id = serializers.CharField()
    status = serializers.CharField()
    amount_due = serializers.IntegerField()
    amount_paid = serializers.IntegerField()
    amount_remaining = serializers.IntegerField()
    currency = serializers.CharField()
    due_date = serializers.DateTimeField()
    invoice_pdf = serializers.URLField()
    created = serializers.DateTimeField()


class PaymentMethodSerializer(serializers.Serializer):
    """Read-only serializer for dj-stripe PaymentMethod objects."""

    id = serializers.CharField()
    type = serializers.CharField()
    card = serializers.SerializerMethodField()
    created = serializers.DateTimeField()

    def get_card(self, obj):
        if obj.card:
            return {
                "brand": obj.card.get("brand", ""),
                "last4": obj.card.get("last4", ""),
                "exp_month": obj.card.get("exp_month"),
                "exp_year": obj.card.get("exp_year"),
            }
        return None


class UsageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageRecord
        fields = ["id", "feature_slug", "quantity", "timestamp", "metadata"]
        read_only_fields = ["id", "timestamp"]


class UsageRecordCreateSerializer(serializers.Serializer):
    feature_slug = serializers.SlugField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    metadata = serializers.DictField(required=False, default=dict)
