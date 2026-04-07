"""dj-stripe webhook signal handlers for Stripe billing events.

Registered in BillingConfig.ready() so they connect at startup.

dj-stripe fires the `webhook_post_process` signal after processing each
incoming Stripe webhook event. We connect a single receiver that dispatches
to event-specific handlers based on the event type.
"""

import logging

from djstripe.signals import webhook_post_process

from apps.billing.models import BillingCustomer

logger = logging.getLogger(__name__)


def _get_billing_customer_for_event(event):
    """Resolve the BillingCustomer from a webhook event's customer field."""
    stripe_customer_id = None
    obj = event.data.get("object", {})

    # Different event types store customer differently
    if "customer" in obj:
        cust = obj["customer"]
        stripe_customer_id = cust if isinstance(cust, str) else cust.get("id")
    elif obj.get("object") == "customer":
        stripe_customer_id = obj.get("id")

    if not stripe_customer_id:
        return None

    return BillingCustomer.objects.filter(
        djstripe_customer__id=stripe_customer_id,
    ).select_related("user", "organization").first()


# ---------------------------------------------------------------------------
# Event-specific handlers
# ---------------------------------------------------------------------------


def _handle_subscription_created(event):
    bc = _get_billing_customer_for_event(event)
    if not bc:
        logger.warning("subscription.created: no BillingCustomer for event %s", event.id)
        return

    from apps.billing.tasks import create_billing_audit_entry, send_billing_notification

    obj = event.data["object"]
    send_billing_notification.delay(
        billing_customer_id=str(bc.id),
        notification_type_slug="billing.subscription.created",
        context={"subscription_id": obj.get("id", "")},
    )
    create_billing_audit_entry.delay(
        billing_customer_id=str(bc.id),
        action="subscription.created",
        metadata={"stripe_subscription_id": obj.get("id", ""), "status": obj.get("status", "")},
    )
    logger.info("subscription.created handled for BillingCustomer %s", bc.id)


def _handle_subscription_updated(event):
    bc = _get_billing_customer_for_event(event)
    if not bc:
        logger.warning("subscription.updated: no BillingCustomer for event %s", event.id)
        return

    from apps.billing.tasks import create_billing_audit_entry, sync_feature_flags_for_customer

    obj = event.data["object"]
    previous = event.data.get("previous_attributes", {})

    create_billing_audit_entry.delay(
        billing_customer_id=str(bc.id),
        action="subscription.updated",
        metadata={
            "stripe_subscription_id": obj.get("id", ""),
            "status": obj.get("status", ""),
            "previous_status": previous.get("status"),
        },
    )

    if "status" in previous or "items" in previous:
        sync_feature_flags_for_customer.delay(billing_customer_id=str(bc.id))

    logger.info("subscription.updated handled for BillingCustomer %s", bc.id)


def _handle_subscription_deleted(event):
    bc = _get_billing_customer_for_event(event)
    if not bc:
        logger.warning("subscription.deleted: no BillingCustomer for event %s", event.id)
        return

    from apps.billing.tasks import (
        create_billing_audit_entry,
        send_billing_notification,
        sync_feature_flags_for_customer,
    )

    obj = event.data["object"]
    send_billing_notification.delay(
        billing_customer_id=str(bc.id),
        notification_type_slug="billing.subscription.canceled",
        context={"subscription_id": obj.get("id", "")},
    )
    create_billing_audit_entry.delay(
        billing_customer_id=str(bc.id),
        action="subscription.deleted",
        metadata={"stripe_subscription_id": obj.get("id", "")},
    )
    sync_feature_flags_for_customer.delay(billing_customer_id=str(bc.id))
    logger.info("subscription.deleted handled for BillingCustomer %s", bc.id)


def _handle_trial_ending(event):
    bc = _get_billing_customer_for_event(event)
    if not bc:
        return

    from apps.billing.tasks import send_billing_notification

    obj = event.data["object"]
    send_billing_notification.delay(
        billing_customer_id=str(bc.id),
        notification_type_slug="billing.trial.ending",
        context={
            "subscription_id": obj.get("id", ""),
            "trial_end": obj.get("trial_end"),
        },
    )
    logger.info("trial_will_end handled for BillingCustomer %s", bc.id)


def _handle_payment_succeeded(event):
    bc = _get_billing_customer_for_event(event)
    if not bc:
        return

    from apps.billing.tasks import create_billing_audit_entry, send_billing_notification

    obj = event.data["object"]
    send_billing_notification.delay(
        billing_customer_id=str(bc.id),
        notification_type_slug="billing.payment.succeeded",
        context={
            "amount_paid": obj.get("amount_paid", 0),
            "currency": obj.get("currency", "usd"),
            "invoice_pdf": obj.get("invoice_pdf", ""),
        },
    )
    create_billing_audit_entry.delay(
        billing_customer_id=str(bc.id),
        action="invoice.payment_succeeded",
        metadata={
            "stripe_invoice_id": obj.get("id", ""),
            "amount_paid": obj.get("amount_paid", 0),
        },
    )


def _handle_payment_failed(event):
    bc = _get_billing_customer_for_event(event)
    if not bc:
        return

    from apps.billing.tasks import create_billing_audit_entry, send_billing_notification

    obj = event.data["object"]
    send_billing_notification.delay(
        billing_customer_id=str(bc.id),
        notification_type_slug="billing.payment.failed",
        context={
            "amount_due": obj.get("amount_due", 0),
            "currency": obj.get("currency", "usd"),
        },
    )
    create_billing_audit_entry.delay(
        billing_customer_id=str(bc.id),
        action="invoice.payment_failed",
        metadata={
            "stripe_invoice_id": obj.get("id", ""),
            "amount_due": obj.get("amount_due", 0),
        },
    )


def _handle_checkout_completed(event):
    obj = event.data.get("object", {})
    billing_customer_id = (obj.get("metadata") or {}).get("billing_customer_id")

    if not billing_customer_id:
        logger.warning("checkout.session.completed: no billing_customer_id in metadata for event %s", event.id)
        return

    from apps.billing.tasks import create_billing_audit_entry

    create_billing_audit_entry.delay(
        billing_customer_id=billing_customer_id,
        action="checkout.session.completed",
        metadata={
            "session_id": obj.get("id", ""),
            "plan_slug": (obj.get("metadata") or {}).get("plan_slug", ""),
        },
    )
    logger.info("checkout.session.completed handled for BillingCustomer %s", billing_customer_id)


# ---------------------------------------------------------------------------
# Dispatcher — maps Stripe event types to handlers
# ---------------------------------------------------------------------------

_EVENT_HANDLERS = {
    "customer.subscription.created": _handle_subscription_created,
    "customer.subscription.updated": _handle_subscription_updated,
    "customer.subscription.deleted": _handle_subscription_deleted,
    "customer.subscription.trial_will_end": _handle_trial_ending,
    "invoice.payment_succeeded": _handle_payment_succeeded,
    "invoice.payment_failed": _handle_payment_failed,
    "checkout.session.completed": _handle_checkout_completed,
}


def _on_webhook_post_process(sender, event, **kwargs):
    """Central dispatcher for dj-stripe webhook events."""
    event_type = event.type if hasattr(event, "type") else ""
    handler = _EVENT_HANDLERS.get(event_type)
    if handler:
        try:
            handler(event)
        except Exception:
            logger.exception("Error handling webhook event %s (type=%s)", event.id, event_type)


# Connect signal — this runs when the module is imported (via apps.py ready())
webhook_post_process.connect(_on_webhook_post_process)
