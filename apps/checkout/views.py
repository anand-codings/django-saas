from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.services import create_checkout_session, get_billing_customer
from apps.checkout.serializers import CheckoutSessionCreateSerializer
from apps.organizations.models import Organization


class CheckoutSessionCreateView(APIView):
    """Create a Stripe Checkout Session for subscription signup.

    POST /api/v1/checkout/create-session/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.plans.models import Plan

        # Resolve plan
        try:
            plan = Plan.objects.get(id=serializer.validated_data["plan_id"], status="active")
        except Plan.DoesNotExist:
            return Response({"detail": "Plan not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        # Resolve billing customer (user or org)
        organization = None
        org_id = serializer.validated_data.get("organization_id")
        if org_id:
            try:
                organization = Organization.objects.get(id=org_id)
            except Organization.DoesNotExist:
                return Response({"detail": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)

        if organization:
            billing_customer = get_billing_customer(organization=organization)
        else:
            billing_customer = get_billing_customer(user=request.user)

        interval = serializer.validated_data["interval"]
        success_url = getattr(settings, "CHECKOUT_SUCCESS_URL", "http://localhost:3000/billing/success?session_id={CHECKOUT_SESSION_ID}")
        cancel_url = getattr(settings, "CHECKOUT_CANCEL_URL", "http://localhost:3000/billing/cancel")

        session = create_checkout_session(
            billing_customer=billing_customer,
            plan=plan,
            interval=interval,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return Response(
            {"checkout_url": session.url, "session_id": session.id},
            status=status.HTTP_200_OK,
        )
