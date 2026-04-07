"""Tests for notifications models."""

import pytest
from django.db import IntegrityError

from apps.notifications.models import Notification, NotificationPreference, NotificationType
from conftest import (
    NotificationFactory,
    NotificationPreferenceFactory,
    NotificationTypeFactory,
    UserFactory,
)


class TestNotificationType:
    def test_create(self):
        nt = NotificationTypeFactory()
        assert nt.pk is not None
        assert nt.is_active is True

    def test_str_returns_slug(self):
        nt = NotificationTypeFactory(slug="invoice.paid")
        assert str(nt) == "invoice.paid"


class TestNotification:
    def test_create(self):
        n = NotificationFactory()
        assert n.pk is not None
        assert n.is_read is False

    def test_str(self):
        n = NotificationFactory(title="Payment received")
        assert "Payment received" in str(n)

    def test_mark_read(self):
        n = NotificationFactory()
        assert n.is_read is False
        assert n.read_at is None
        n.mark_read()
        n.refresh_from_db()
        assert n.is_read is True
        assert n.read_at is not None

    def test_ordering_newest_first(self):
        user = UserFactory()
        n1 = NotificationFactory(recipient=user, title="First")
        n2 = NotificationFactory(recipient=user, title="Second")
        notifications = list(Notification.objects.filter(recipient=user))
        assert notifications[0] == n2
        assert notifications[1] == n1


class TestNotificationPreference:
    def test_create(self):
        pref = NotificationPreferenceFactory()
        assert pref.pk is not None
        assert pref.channels == ["in_app", "email"]

    def test_str(self):
        pref = NotificationPreferenceFactory()
        assert str(pref.notification_type.slug) in str(pref)

    def test_unique_user_notification_pref(self):
        user = UserFactory()
        nt = NotificationTypeFactory()
        NotificationPreferenceFactory(user=user, notification_type=nt)
        with pytest.raises(IntegrityError):
            NotificationPreferenceFactory(user=user, notification_type=nt)
