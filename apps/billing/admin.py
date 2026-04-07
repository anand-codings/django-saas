from django.contrib import admin

from apps.billing.models import BillingCustomer, UsageRecord


@admin.register(BillingCustomer)
class BillingCustomerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "djstripe_customer", "created_at")
    search_fields = ("user__email", "organization__name")
    raw_id_fields = ("user", "organization", "djstripe_customer")


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ("subscription", "feature_slug", "quantity", "timestamp")
    search_fields = ("feature_slug",)
    list_filter = ("feature_slug",)
    raw_id_fields = ("subscription",)
