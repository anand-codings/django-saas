"""Tests for billing API views."""

import pytest
from django.urls import reverse
from rest_framework import status

from apps.billing.models import BillingCustomer
from conftest import BillingCustomerFactory, UserFactory


class TestBillingCustomerViewSet:
    def test_get_or_create_customer(self, authenticated_client, user):
        url = reverse("billing:customer")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert BillingCustomer.objects.filter(user=user).exists()

    def test_unauthenticated(self, api_client):
        url = reverse("billing:customer")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_existing_customer(self, authenticated_client, user):
        BillingCustomerFactory(user=user)
        url = reverse("billing:customer")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert BillingCustomer.objects.filter(user=user).count() == 1
