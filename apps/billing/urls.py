from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.billing.views import (
    BillingCustomerViewSet,
    InvoiceViewSet,
    PaymentMethodViewSet,
    SubscriptionViewSet,
    UsageRecordViewSet,
)

app_name = "billing"

router = DefaultRouter()
router.register("subscriptions", SubscriptionViewSet, basename="subscription")
router.register("invoices", InvoiceViewSet, basename="invoice")
router.register("payment-methods", PaymentMethodViewSet, basename="payment-method")
router.register("usage", UsageRecordViewSet, basename="usage")

urlpatterns = [
    path("customer/", BillingCustomerViewSet.as_view({"get": "retrieve"}), name="customer"),
    path("", include(router.urls)),
]
