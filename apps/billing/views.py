from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.billing.models import (
    BillingCustomer,
    Invoice,
    PaymentMethod,
    Subscription,
    UsageRecord,
)
from apps.billing.serializers import (
    BillingCustomerSerializer,
    InvoiceSerializer,
    PaymentMethodSerializer,
    SubscriptionCancelSerializer,
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
    UsageRecordCreateSerializer,
    UsageRecordSerializer,
)


class BillingCustomerViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """GET the current user's billing customer profile."""

    serializer_class = BillingCustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        customer, _ = BillingCustomer.objects.get_or_create(
            user=self.request.user,
            defaults={"email": self.request.user.email, "name": self.request.user.get_full_name()},
        )
        return customer


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve subscriptions for the current user."""

    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(customer__user=self.request.user)

    @action(detail=False, methods=["post"], serializer_class=SubscriptionCreateSerializer)
    def subscribe(self, request):
        """Create a new subscription."""
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Delegate to payment provider in a real implementation
        return Response({"detail": "Subscription creation delegated to payment provider."}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"], serializer_class=SubscriptionCancelSerializer)
    def cancel(self, request, pk=None):
        """Cancel a subscription."""
        subscription = self.get_object()
        serializer = SubscriptionCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Delegate to payment provider
        return Response({"detail": "Cancellation delegated to payment provider."}, status=status.HTTP_202_ACCEPTED)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve invoices."""

    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(customer__user=self.request.user)


class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """List payment methods."""

    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(customer__user=self.request.user)


class UsageRecordViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """List and record usage."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UsageRecordCreateSerializer
        return UsageRecordSerializer

    def get_queryset(self):
        return UsageRecord.objects.filter(subscription__customer__user=self.request.user)
