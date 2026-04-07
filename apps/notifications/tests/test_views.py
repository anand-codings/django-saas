"""Tests for notifications API views."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory

from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.views import NotificationPreferenceViewSet
from conftest import NotificationFactory, NotificationPreferenceFactory, NotificationTypeFactory, UserFactory


class TestNotificationViewSet:
    def test_list_own_notifications(self, authenticated_client, user):
        NotificationFactory(recipient=user)
        NotificationFactory(recipient=user)
        other = UserFactory()
        NotificationFactory(recipient=other)
        url = reverse("app_notifications:notification-list")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_filter_by_is_read(self, authenticated_client, user):
        NotificationFactory(recipient=user, is_read=False)
        n2 = NotificationFactory(recipient=user)
        n2.mark_read()
        url = reverse("app_notifications:notification-list")
        response = authenticated_client.get(url, {"is_read": "false"})
        assert len(response.data["results"]) == 1

    def test_read_action(self, authenticated_client, user):
        n = NotificationFactory(recipient=user)
        url = reverse("app_notifications:notification-read", kwargs={"pk": n.pk})
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        n.refresh_from_db()
        assert n.is_read is True

    def test_mark_read_bulk(self, authenticated_client, user):
        n1 = NotificationFactory(recipient=user)
        n2 = NotificationFactory(recipient=user)
        url = reverse("app_notifications:notification-mark-read")
        response = authenticated_client.post(url, {"notification_ids": [str(n1.pk), str(n2.pk)]}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["marked_read"] == 2

    def test_mark_read_all(self, authenticated_client, user):
        NotificationFactory(recipient=user)
        NotificationFactory(recipient=user)
        url = reverse("app_notifications:notification-mark-read")
        response = authenticated_client.post(url, {"all": True}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["marked_read"] == 2

    def test_unread_count(self, authenticated_client, user):
        NotificationFactory(recipient=user)
        n2 = NotificationFactory(recipient=user)
        n2.mark_read()
        url = reverse("app_notifications:notification-unread-count")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["unread_count"] == 1

    def test_unauthenticated(self, api_client):
        url = reverse("app_notifications:notification-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationPreferenceViewSet:
    """Uses APIRequestFactory because preferences URL conflicts with notification pk router."""

    def test_create_preference(self):
        user = UserFactory()
        nt = NotificationTypeFactory()
        factory = APIRequestFactory()
        request = factory.post(
            "/preferences/",
            {"notification_type": str(nt.pk), "channels": ["in_app", "email"]},
            format="json",
        )
        request.user = user
        view = NotificationPreferenceViewSet.as_view({"post": "create"})
        response = view(request)
        assert response.status_code == status.HTTP_201_CREATED
        assert NotificationPreference.objects.filter(user=user).exists()

    def test_list_own_preferences(self):
        user = UserFactory()
        nt = NotificationTypeFactory()
        NotificationPreferenceFactory(user=user, notification_type=nt)
        other = UserFactory()
        NotificationPreferenceFactory(user=other)

        factory = APIRequestFactory()
        request = factory.get("/preferences/")
        request.user = user
        view = NotificationPreferenceViewSet.as_view({"get": "list"})
        response = view(request)
        response.render()
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        assert len(results) == 1
