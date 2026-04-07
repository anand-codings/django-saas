"""Seed NotificationType records for billing events."""

from django.core.management.base import BaseCommand

from apps.notifications.models import NotificationType

BILLING_NOTIFICATION_TYPES = [
    {
        "slug": "billing.subscription.created",
        "name": "Subscription Created",
        "category": "billing",
        "default_channels": ["in_app", "email"],
        "title_template": "Welcome to your new subscription!",
        "body_template": "Your subscription is now active. You can manage it from your billing settings.",
    },
    {
        "slug": "billing.subscription.canceled",
        "name": "Subscription Canceled",
        "category": "billing",
        "default_channels": ["in_app", "email"],
        "title_template": "Your subscription has been canceled",
        "body_template": (
            "Your subscription has been canceled."
            " You will retain access until the end of your current billing period."
        ),
    },
    {
        "slug": "billing.trial.ending",
        "name": "Trial Ending Soon",
        "category": "billing",
        "default_channels": ["in_app", "email"],
        "title_template": "Your trial ends in 3 days",
        "body_template": "Your free trial is ending soon. Add a payment method to continue uninterrupted access.",
    },
    {
        "slug": "billing.payment.succeeded",
        "name": "Payment Succeeded",
        "category": "billing",
        "default_channels": ["in_app", "email"],
        "title_template": "Payment received",
        "body_template": "We received your payment. Thank you!",
    },
    {
        "slug": "billing.payment.failed",
        "name": "Payment Failed",
        "category": "billing",
        "default_channels": ["in_app", "email"],
        "title_template": "Payment failed",
        "body_template": (
            "We were unable to process your payment."
            " Please update your payment method to avoid service interruption."
        ),
    },
]


class Command(BaseCommand):
    help = "Create or update NotificationType records for billing events."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for data in BILLING_NOTIFICATION_TYPES:
            _, created = NotificationType.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "category": data["category"],
                    "default_channels": data["default_channels"],
                    "title_template": data["title_template"],
                    "body_template": data["body_template"],
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done: {created_count} created, {updated_count} updated."
        ))
