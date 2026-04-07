from django.shortcuts import get_object_or_404
from djstripe.models import Invoice as DjstripeInvoice
from djstripe.models import PaymentMethod as DjstripePaymentMethod
from djstripe.models import Subscription as DjstripeSubscription
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.billing.models import BillingCustomer, UsageRecord
from apps.billing.permissions import HasBillingAccess
from apps.billing.serializers import (
    BillingCustomerSerializer,
    InvoiceSerializer,
    PaymentMethodSerializer,
    SubscriptionCancelSerializer,
    SubscriptionSerializer,
    UsageRecordCreateSerializer,
    UsageRecordSerializer,
)
from apps.billing.services import (
    cancel_subscription,
    reactivate_subscription,
)


class BillingCustomerViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """GET the current user's billing customer profile."""

    serializer_class = BillingCustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        customer, _ = BillingCustomer.objects.get_or_create(user=self.request.user)
        return customer


class SubscriptionViewSet(viewsets.ViewSet):
    """List, cancel, and reactivate subscriptions via dj-stripe."""

    permission_classes = [permissions.IsAuthenticated, HasBillingAccess]

    def _get_customer(self, request):
        try:
            return BillingCustomer.objects.select_related("djstripe_customer").get(user=request.user)
        except BillingCustomer.DoesNotExist:
            return None

    def list(self, request):
        bc = self._get_customer(request)
        if not bc or not bc.djstripe_customer:
            return Response([])

        subs = DjstripeSubscription.objects.filter(
            customer=bc.djstripe_customer,
        ).select_related("plan", "plan__product").order_by("-created")
        serializer = SubscriptionSerializer(subs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        bc = self._get_customer(request)
        if not bc or not bc.djstripe_customer:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        sub = get_object_or_404(
            DjstripeSubscription,
            id=pk,
            customer=bc.djstripe_customer,
        )
        serializer = SubscriptionSerializer(sub)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a subscription."""
        bc = self._get_customer(request)
        if not bc or not bc.djstripe_customer:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        sub = get_object_or_404(
            DjstripeSubscription,
            id=pk,
            customer=bc.djstripe_customer,
        )

        serializer = SubscriptionCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cancel_subscription(sub.id, at_period_end=serializer.validated_data["at_period_end"])
        return Response({"detail": "Cancellation requested."}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"])
    def reactivate(self, request, pk=None):
        """Reactivate a subscription that was scheduled for cancellation."""
        bc = self._get_customer(request)
        if not bc or not bc.djstripe_customer:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        sub = get_object_or_404(
            DjstripeSubscription,
            id=pk,
            customer=bc.djstripe_customer,
            cancel_at_period_end=True,
            status="active",
        )

        reactivate_subscription(sub.id)
        return Response({"detail": "Subscription reactivated."}, status=status.HTTP_200_OK)


class InvoiceViewSet(viewsets.ViewSet):
    """Read-only list of invoices from dj-stripe."""

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        try:
            bc = BillingCustomer.objects.select_related("djstripe_customer").get(user=request.user)
        except BillingCustomer.DoesNotExist:
            return Response([])

        if not bc.djstripe_customer:
            return Response([])

        invoices = DjstripeInvoice.objects.filter(
            customer=bc.djstripe_customer,
        ).order_by("-created")
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


class PaymentMethodViewSet(viewsets.ViewSet):
    """Read-only list of payment methods from dj-stripe."""

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        try:
            bc = BillingCustomer.objects.select_related("djstripe_customer").get(user=request.user)
        except BillingCustomer.DoesNotExist:
            return Response([])

        if not bc.djstripe_customer:
            return Response([])

        methods = DjstripePaymentMethod.objects.filter(
            customer=bc.djstripe_customer,
        ).order_by("-created")
        serializer = PaymentMethodSerializer(methods, many=True)
        return Response(serializer.data)


class UsageRecordViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """List and record usage."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UsageRecordCreateSerializer
        return UsageRecordSerializer

    def get_queryset(self):
        return UsageRecord.objects.filter(
            subscription__customer__subscriber=self.request.user,
        )
