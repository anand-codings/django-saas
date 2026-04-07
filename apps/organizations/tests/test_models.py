"""Tests for organizations models."""

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.organizations.models import Membership, Organization, OrganizationInvite
from conftest import MembershipFactory, OrganizationFactory, OrganizationInviteFactory, UserFactory
from shared.types.enums import MembershipRole


class TestOrganization:
    def test_create(self):
        org = OrganizationFactory()
        assert org.pk is not None
        assert org.status == "active"

    def test_str_returns_name(self):
        org = OrganizationFactory(name="Acme Inc")
        assert str(org) == "Acme Inc"

    def test_slug_unique(self):
        OrganizationFactory(slug="acme")
        with pytest.raises(IntegrityError):
            OrganizationFactory(slug="acme")

    def test_auto_creates_owner_membership(self):
        org = OrganizationFactory()
        membership = Membership.objects.get(user=org.owner, organization=org)
        assert membership.role == MembershipRole.OWNER
        assert membership.is_active is True


class TestMembership:
    def test_create(self):
        org = OrganizationFactory()
        user = UserFactory()
        m = MembershipFactory(user=user, organization=org, role="member")
        assert m.pk is not None

    def test_str(self):
        m = MembershipFactory()
        assert str(m.organization) in str(m)

    def test_unique_user_organization(self):
        org = OrganizationFactory()
        user = UserFactory()
        MembershipFactory(user=user, organization=org)
        with pytest.raises(IntegrityError):
            MembershipFactory(user=user, organization=org)


class TestOrganizationInvite:
    def test_create(self):
        invite = OrganizationInviteFactory()
        assert invite.pk is not None
        assert invite.token

    def test_str(self):
        invite = OrganizationInviteFactory()
        assert invite.email in str(invite)

    def test_is_expired_false_when_future(self):
        invite = OrganizationInviteFactory(expires_at=timezone.now() + timedelta(days=1))
        assert invite.is_expired is False

    def test_is_expired_true_when_past(self):
        invite = OrganizationInviteFactory(expires_at=timezone.now() - timedelta(hours=1))
        assert invite.is_expired is True

    def test_is_acceptable_when_pending_and_not_expired(self):
        invite = OrganizationInviteFactory(
            status="pending", expires_at=timezone.now() + timedelta(days=1)
        )
        assert invite.is_acceptable is True

    def test_is_acceptable_false_when_revoked(self):
        invite = OrganizationInviteFactory(
            status="revoked", expires_at=timezone.now() + timedelta(days=1)
        )
        assert invite.is_acceptable is False

    def test_is_acceptable_false_when_expired(self):
        invite = OrganizationInviteFactory(
            status="pending", expires_at=timezone.now() - timedelta(hours=1)
        )
        assert invite.is_acceptable is False
