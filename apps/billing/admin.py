from django.contrib import admin

from apps.billing.models import (
    BillingCustomer,
    Invoice,
    PaymentMethod,
    Subscription,
    UsageRecord,
)


@admin.register(BillingCustomer)
class BillingCustomerAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "provider", "currency", "created_at")
    search_fields = ("email", "name", "stripe_customer_id")
    list_filter = ("provider", "currency")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("customer", "plan", "status", "interval", "current_period_end", "created_at")
    search_fields = ("customer__email", "stripe_subscription_id")
    list_filter = ("status", "interval")
    raw_id_fields = ("customer", "plan")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("customer", "amount_due", "currency", "status", "due_date", "paid_at")
    search_fields = ("customer__email", "stripe_invoice_id")
    list_filter = ("status", "currency")
    raw_id_fields = ("customer", "subscription")


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("customer", "card_brand", "card_last4", "is_default", "created_at")
    list_filter = ("card_brand", "is_default")
    raw_id_fields = ("customer",)


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ("subscription", "feature_slug", "quantity", "timestamp")
    search_fields = ("feature_slug",)
    list_filter = ("feature_slug",)
    raw_id_fields = ("subscription",)
