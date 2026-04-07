"""Tests for tenancy models."""

import pytest
from django.db import IntegrityError

from apps.tenancy.models import Tenant, TenantMembership
from conftest import TenantFactory, TenantMembershipFactory, UserFactory


class TestTenant:
    def test_create(self):
        tenant = TenantFactory()
        assert tenant.pk is not None
        assert tenant.status == "active"

    def test_str_returns_name(self):
        tenant = TenantFactory(name="Acme")
        assert str(tenant) == "Acme"

    def test_slug_unique(self):
        TenantFactory(slug="acme")
        with pytest.raises(IntegrityError):
            TenantFactory(slug="acme")

    def test_default_settings_empty_dict(self):
        tenant = TenantFactory()
        assert tenant.settings == {}


class TestTenantMembership:
    def test_create(self):
        tm = TenantMembershipFactory()
        assert tm.pk is not None
        assert tm.role == "member"

    def test_str(self):
        tm = TenantMembershipFactory()
        assert tm.tenant.name in str(tm)

    def test_unique_tenant_user(self):
        tenant = TenantFactory()
        user = UserFactory()
        TenantMembershipFactory(tenant=tenant, user=user)
        with pytest.raises(IntegrityError):
            TenantMembershipFactory(tenant=tenant, user=user)

    def test_is_default_false_by_default(self):
        tm = TenantMembershipFactory()
        assert tm.is_default is False
