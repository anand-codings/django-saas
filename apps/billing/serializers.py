from rest_framework import serializers

from apps.billing.models import (
    BillingCustomer,
    Invoice,
    PaymentMethod,
    Subscription,
    UsageRecord,
)
from apps.plans.models import Plan


class BillingCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingCustomer
        fields = ["id", "email", "name", "currency", "provider", "created_at"]
        read_only_fields = ["id", "provider", "created_at"]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id", "customer", "plan", "plan_name", "status", "interval", "quantity",
            "current_period_start", "current_period_end",
            "trial_start", "trial_end",
            "cancel_at_period_end", "canceled_at",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]


class SubscriptionCreateSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField()
    interval = serializers.ChoiceField(choices=["monthly", "yearly"], default="monthly")
    trial_days = serializers.IntegerField(default=0, min_value=0)


class SubscriptionCancelSerializer(serializers.Serializer):
    at_period_end = serializers.BooleanField(default=True)


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id", "customer", "subscription", "amount_due", "amount_paid", "amount_remaining",
            "currency", "status", "due_date", "paid_at", "invoice_pdf_url",
            "line_items", "created_at",
        ]
        read_only_fields = fields


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            "id", "card_brand", "card_last4", "card_exp_month", "card_exp_year",
            "is_default", "created_at",
        ]
        read_only_fields = fields


class UsageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageRecord
        fields = ["id", "feature_slug", "quantity", "timestamp", "metadata"]
        read_only_fields = ["id", "timestamp"]


class UsageRecordCreateSerializer(serializers.Serializer):
    feature_slug = serializers.SlugField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    metadata = serializers.DictField(required=False, default=dict)
