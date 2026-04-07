"""Tests for billing models."""

import pytest
from django.db import IntegrityError

from apps.billing.models import BillingCustomer
from conftest import BillingCustomerFactory, OrganizationFactory, UserFactory


class TestBillingCustomer:
    def test_create_with_user(self):
        bc = BillingCustomerFactory()
        assert bc.pk is not None
        assert bc.user is not None
        assert bc.organization is None

    def test_create_with_org(self):
        org = OrganizationFactory()
        bc = BillingCustomerFactory(user=None, organization=org)
        assert bc.pk is not None
        assert bc.user is None
        assert bc.organization == org

    def test_str_for_user(self):
        user = UserFactory(email="bill@example.com")
        bc = BillingCustomerFactory(user=user)
        assert "bill@example.com" in str(bc)

    def test_str_for_org(self):
        org = OrganizationFactory(name="Acme")
        bc = BillingCustomerFactory(user=None, organization=org)
        assert "Acme" in str(bc)

    def test_subscriber_email_for_user(self):
        user = UserFactory(email="pay@example.com")
        bc = BillingCustomerFactory(user=user)
        assert bc.subscriber_email == "pay@example.com"

    def test_subscriber_email_for_org(self):
        org = OrganizationFactory()
        bc = BillingCustomerFactory(user=None, organization=org)
        assert bc.subscriber_email == org.owner.email

    def test_subscriber_name_for_user(self):
        user = UserFactory(first_name="Jane", last_name="Doe")
        bc = BillingCustomerFactory(user=user)
        assert bc.subscriber_name == "Jane Doe"

    def test_subscriber_name_for_org(self):
        org = OrganizationFactory(name="Acme")
        bc = BillingCustomerFactory(user=None, organization=org)
        assert bc.subscriber_name == "Acme"
