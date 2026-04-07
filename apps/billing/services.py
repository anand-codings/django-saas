"""Business logic for billing — bridges our domain models with dj-stripe and Stripe API."""

import logging

import stripe
from django.db.models import Q
from djstripe.models import Customer as DjstripeCustomer
from djstripe.models import Subscription as DjstripeSubscription
from shared.types.enums import MembershipRole

from apps.billing.models import BillingCustomer
from apps.organizations.models import Membership
from apps.plans.models import Plan

logger = logging.getLogger(__name__)


def get_billing_customer(user=None, organization=None):
    """Get or create a BillingCustomer and ensure a linked Stripe customer exists.

    Exactly one of user or organization must be provided.
    """
    if user and organization:
        raise ValueError("Provide user or organization, not both.")
    if not user and not organization:
        raise ValueError("Provide either user or organization.")

    if organization:
        billing_customer, created = BillingCustomer.objects.get_or_create(
            organization=organization,
        )
        email = organization.owner.email if organization.owner else ""
        name = organization.name
    else:
        billing_customer, created = BillingCustomer.objects.get_or_create(
            user=user,
        )
        email = user.email
        name = user.get_full_name()

    # Ensure a Stripe customer is linked
    if not billing_customer.djstripe_customer:
        stripe_customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                "billing_customer_id": str(billing_customer.id),
                "type": "organization" if organization else "user",
            },
        )
        djstripe_customer = DjstripeCustomer.sync_from_stripe_data(stripe_customer)
        billing_customer.djstripe_customer = djstripe_customer
        billing_customer.save(update_fields=["djstripe_customer", "updated_at"])

    return billing_customer


def get_active_subscription(user=None, organization=None):
    """Return the active dj-stripe Subscription for a user or organization, or None."""
    if organization:
        bc = BillingCustomer.objects.filter(organization=organization).select_related("djstripe_customer").first()
    elif user:
        bc = BillingCustomer.objects.filter(user=user).select_related("djstripe_customer").first()
    else:
        return None

    if not bc or not bc.djstripe_customer:
        return None

    return (
        DjstripeSubscription.objects.filter(
            customer=bc.djstripe_customer,
            status__in=["active", "trialing"],
        )
        .select_related("plan", "plan__product")
        .first()
    )


def cancel_subscription(subscription_id, at_period_end=True):
    """Cancel a Stripe subscription.

    Args:
        subscription_id: The Stripe subscription ID (e.g., sub_xxx).
        at_period_end: If True, cancel at period end. If False, cancel immediately.
    """
    if at_period_end:
        return stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
    else:
        return stripe.Subscription.cancel(subscription_id)


def reactivate_subscription(subscription_id):
    """Reactivate a subscription that was scheduled for cancellation."""
    return stripe.Subscription.modify(subscription_id, cancel_at_period_end=False)


def create_checkout_session(billing_customer, plan, interval, success_url, cancel_url):
    """Create a Stripe Checkout Session for a subscription.

    Args:
        billing_customer: BillingCustomer instance with linked djstripe_customer.
        plan: Plan instance.
        interval: "monthly" or "yearly".
        success_url: URL to redirect on success.
        cancel_url: URL to redirect on cancel.

    Returns:
        stripe.checkout.Session object.
    """
    price_id = plan.stripe_monthly_price_id if interval == "monthly" else plan.stripe_yearly_price_id
    if not price_id:
        raise ValueError(f"Plan '{plan.name}' has no Stripe price for interval '{interval}'.")

    session_params = {
        "customer": billing_customer.djstripe_customer.id,
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": {
            "billing_customer_id": str(billing_customer.id),
            "plan_slug": plan.slug,
        },
    }

    if plan.trial_days > 0:
        session_params["subscription_data"] = {
            "trial_period_days": plan.trial_days,
        }

    return stripe.checkout.Session.create(**session_params)


def get_plan_from_stripe_price(price_id):
    """Resolve a Plan from a Stripe price ID, or None."""
    return Plan.objects.filter(
        Q(stripe_monthly_price_id=price_id) | Q(stripe_yearly_price_id=price_id)
    ).first()


def user_has_billing_access(user, billing_customer):
    """Check if a user has billing access to a BillingCustomer."""
    if billing_customer.user_id:
        return billing_customer.user_id == user.pk

    if billing_customer.organization_id:
        return Membership.objects.filter(
            user=user,
            organization_id=billing_customer.organization_id,
            role__in=[MembershipRole.OWNER, MembershipRole.ADMIN, MembershipRole.BILLING],
            is_active=True,
        ).exists()

    return False
