"""Tests for billing Celery tasks."""

import pytest

from apps.billing.tasks import create_billing_audit_entry, send_billing_notification
from apps.notifications.models import Notification
from conftest import BillingCustomerFactory, NotificationTypeFactory, UserFactory


class TestSendBillingNotification:
    def test_creates_notification(self):
        user = UserFactory()
        bc = BillingCustomerFactory(user=user)
        nt = NotificationTypeFactory(slug="invoice.paid")
        send_billing_notification(str(bc.pk), "invoice.paid")
        assert Notification.objects.filter(recipient=user, notification_type=nt).exists()

    def test_missing_billing_customer(self):
        """Task should return without error for nonexistent customer."""
        import uuid

        send_billing_notification(str(uuid.uuid4()), "invoice.paid")

    def test_inactive_notification_type(self):
        user = UserFactory()
        bc = BillingCustomerFactory(user=user)
        NotificationTypeFactory(slug="invoice.paid", is_active=False)
        send_billing_notification(str(bc.pk), "invoice.paid")
        assert Notification.objects.count() == 0

    def test_org_billing_customer(self):
        """Notification goes to the org owner."""
        from conftest import OrganizationFactory

        org = OrganizationFactory()
        bc = BillingCustomerFactory(user=None, organization=org)
        nt = NotificationTypeFactory(slug="subscription.renewed")
        send_billing_notification(str(bc.pk), "subscription.renewed")
        assert Notification.objects.filter(recipient=org.owner).exists()


class TestCreateBillingAuditEntry:
    def test_logs_without_error(self):
        bc = BillingCustomerFactory()
        create_billing_audit_entry(str(bc.pk), "subscription.created", {"plan": "pro"})

    def test_missing_customer(self):
        import uuid

        create_billing_audit_entry(str(uuid.uuid4()), "subscription.created")
