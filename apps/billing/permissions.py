"""Billing-specific DRF permissions."""

from rest_framework.permissions import BasePermission

from apps.billing.services import user_has_billing_access


class HasBillingAccess(BasePermission):
    """Checks that the user owns the BillingCustomer or has a billing role in the org."""

    def has_object_permission(self, request, view, obj):
        # obj can be a BillingCustomer or an object with a billing_customer-like resolution
        from apps.billing.models import BillingCustomer

        if isinstance(obj, BillingCustomer):
            return user_has_billing_access(request.user, obj)

        # For dj-stripe objects (Subscription, Invoice, PaymentMethod), resolve via customer
        customer = getattr(obj, "customer", None)
        if customer:
            bc = BillingCustomer.objects.filter(djstripe_customer=customer).first()
            if bc:
                return user_has_billing_access(request.user, bc)

        return False
