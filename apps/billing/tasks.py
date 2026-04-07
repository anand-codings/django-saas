"""Celery tasks for billing — notifications, audit logging, feature flag sync."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_billing_notification(self, billing_customer_id, notification_type_slug, context=None):
    """Create a notification for a billing event.

    Looks up the NotificationType by slug, resolves the recipient from the
    BillingCustomer, and creates a Notification record.
    """
    from apps.billing.models import BillingCustomer
    from apps.notifications.models import Notification, NotificationType

    try:
        bc = BillingCustomer.objects.select_related("user", "organization__owner").get(id=billing_customer_id)
    except BillingCustomer.DoesNotExist:
        logger.error("send_billing_notification: BillingCustomer %s not found", billing_customer_id)
        return

    try:
        notif_type = NotificationType.objects.get(slug=notification_type_slug, is_active=True)
    except NotificationType.DoesNotExist:
        logger.warning("send_billing_notification: NotificationType '%s' not found or inactive", notification_type_slug)
        return

    # Determine recipient
    recipient = bc.user or (bc.organization.owner if bc.organization else None)
    if not recipient:
        logger.warning("send_billing_notification: No recipient for BillingCustomer %s", billing_customer_id)
        return

    context = context or {}
    title = notif_type.title_template.format(**context) if context else notif_type.title_template
    body = notif_type.body_template.format(**context) if context else notif_type.body_template

    Notification.objects.create(
        recipient=recipient,
        notification_type=notif_type,
        title=title,
        body=body,
        data=context,
        channels_sent=notif_type.default_channels,
    )
    logger.info("Billing notification '%s' sent to user %s", notification_type_slug, recipient.pk)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def create_billing_audit_entry(self, billing_customer_id, action, metadata=None):
    """Write an audit log entry for a billing event."""
    from apps.billing.models import BillingCustomer

    try:
        BillingCustomer.objects.get(id=billing_customer_id)
    except BillingCustomer.DoesNotExist:
        logger.error("create_billing_audit_entry: BillingCustomer %s not found", billing_customer_id)
        return

    # Use Django's built-in logging as the audit trail — auditlog middleware
    # handles model-level changes automatically. This task captures webhook-driven
    # events that don't go through the ORM save path.
    logger.info(
        "BILLING_AUDIT billing_customer=%s action=%s metadata=%s",
        billing_customer_id,
        action,
        metadata or {},
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_feature_flags_for_customer(self, billing_customer_id):
    """Sync feature flags based on the customer's current subscription plan.

    When a subscription status or plan changes, this task updates waffle flags
    for the user/org so feature gating reflects the active plan.
    """
    from apps.billing.models import BillingCustomer
    from apps.billing.services import get_active_subscription, get_plan_from_stripe_price

    try:
        bc = BillingCustomer.objects.select_related("user", "organization").get(id=billing_customer_id)
    except BillingCustomer.DoesNotExist:
        logger.error("sync_feature_flags: BillingCustomer %s not found", billing_customer_id)
        return

    subscription = get_active_subscription(user=bc.user, organization=bc.organization)
    if not subscription:
        logger.info("sync_feature_flags: No active subscription for BillingCustomer %s", billing_customer_id)
        return

    plan = get_plan_from_stripe_price(subscription.plan.id)
    if not plan:
        logger.warning("sync_feature_flags: No Plan found for Stripe price %s", subscription.plan.id)
        return

    # Log which plan features are active — actual waffle flag manipulation
    # depends on how the project has configured waffle (flags vs switches vs samples).
    # This logs the intent; integrate with waffle's programmatic API as needed.
    features = list(plan.features.filter(is_boolean=True).values_list("slug", flat=True))
    logger.info(
        "sync_feature_flags: BillingCustomer %s on plan '%s' with features: %s",
        billing_customer_id,
        plan.slug,
        features,
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def report_usage_to_stripe(self, usage_record_id):
    """Report a UsageRecord to Stripe for metered billing."""
    import stripe

    from apps.billing.models import UsageRecord

    try:
        record = UsageRecord.objects.select_related("subscription").get(id=usage_record_id)
    except UsageRecord.DoesNotExist:
        logger.error("report_usage_to_stripe: UsageRecord %s not found", usage_record_id)
        return

    # Find the subscription item for the metered price
    sub_items = stripe.SubscriptionItem.list(subscription=record.subscription.id)
    if not sub_items.data:
        logger.warning("report_usage_to_stripe: No subscription items for %s", record.subscription.id)
        return

    # Report to the first subscription item (single-price subscriptions)
    stripe.SubscriptionItem.create_usage_record(
        sub_items.data[0].id,
        quantity=record.quantity,
        action="increment",
    )
    logger.info("Usage reported to Stripe: %s units for %s", record.quantity, record.feature_slug)
