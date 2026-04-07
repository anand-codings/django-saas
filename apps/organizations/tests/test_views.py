from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory

from apps.accounts.models import User
from apps.organizations.models import Membership, Organization
from apps.organizations.views import MembershipViewSet
from shared.types.enums import MembershipRole


class MembershipDeleteLastOwnerTest(TestCase):
    """Verify that deleting the last owner of an organization is blocked."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="testpass1234"
        )
        self.org = Organization.objects.create(
            name="Test Org", slug="test-org", owner=self.owner
        )
        # Signal auto-creates OWNER membership; fetch it.
        self.membership = Membership.objects.get(
            user=self.owner, organization=self.org
        )

    def test_cannot_delete_last_owner(self):
        """perform_destroy must raise ValidationError for the last owner."""
        factory = APIRequestFactory()
        request = factory.delete(f"/api/v1/organizations/test-org/members/{self.membership.pk}/")
        request.user = self.owner

        view = MembershipViewSet.as_view({"delete": "destroy"})
        response = view(
            request,
            organization_slug="test-org",
            pk=self.membership.pk,
        )

        # Should get 400, not 204 — the deletion must be blocked
        self.assertEqual(response.status_code, 400)
        # Owner membership should still exist
        self.assertTrue(
            Membership.objects.filter(pk=self.membership.pk).exists()
        )

    def test_can_delete_owner_when_another_exists(self):
        """Deleting an owner is fine if another owner remains."""
        other_owner = User.objects.create_user(
            username="owner2", email="owner2@example.com", password="testpass1234"
        )
        Membership.objects.create(
            user=other_owner,
            organization=self.org,
            role=MembershipRole.OWNER,
            is_active=True,
        )

        factory = APIRequestFactory()
        request = factory.delete(f"/api/v1/organizations/test-org/members/{self.membership.pk}/")
        request.user = self.owner

        view = MembershipViewSet.as_view({"delete": "destroy"})
        response = view(
            request,
            organization_slug="test-org",
            pk=self.membership.pk,
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Membership.objects.filter(pk=self.membership.pk).exists()
        )


# ---------------------------------------------------------------------------
# pytest-style API tests
# ---------------------------------------------------------------------------

import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone as tz
from rest_framework import status as http_status
from conftest import (
    MembershipFactory,
    OrganizationFactory,
    OrganizationInviteFactory,
    UserFactory,
)


class TestOrganizationViewSetAPI:
    def test_list_own_orgs(self, api_client):
        user = UserFactory()
        org = OrganizationFactory(owner=user)
        other_org = OrganizationFactory()  # user is not a member
        api_client.force_authenticate(user=user)
        url = reverse("organizations:organization-list")
        response = api_client.get(url)
        assert response.status_code == http_status.HTTP_200_OK
        slugs = [o["slug"] for o in response.data["results"]]
        assert org.slug in slugs
        assert other_org.slug not in slugs

    def test_create_org(self, api_client):
        user = UserFactory()
        api_client.force_authenticate(user=user)
        url = reverse("organizations:organization-list")
        data = {"name": "New Org", "slug": "new-org"}
        response = api_client.post(url, data)
        assert response.status_code == http_status.HTTP_201_CREATED
        assert Membership.objects.filter(user=user, organization__slug="new-org", role="owner").exists()


class TestInviteViewSetAPI:
    def test_accept_invite(self, api_client):
        org = OrganizationFactory()
        invitee = UserFactory(email="invitee@example.com")
        invite = OrganizationInviteFactory(
            organization=org,
            email="invitee@example.com",
            expires_at=tz.now() + timedelta(days=7),
        )
        api_client.force_authenticate(user=invitee)
        url = reverse(
            "organizations:invite-accept",
            kwargs={"organization_slug": org.slug, "token": invite.token},
        )
        response = api_client.post(url)
        assert response.status_code == http_status.HTTP_200_OK
        assert Membership.objects.filter(user=invitee, organization=org).exists()

    def test_accept_expired_invite(self, api_client):
        org = OrganizationFactory()
        invitee = UserFactory(email="exp@example.com")
        invite = OrganizationInviteFactory(
            organization=org,
            email="exp@example.com",
            expires_at=tz.now() - timedelta(hours=1),
        )
        api_client.force_authenticate(user=invitee)
        url = reverse(
            "organizations:invite-accept",
            kwargs={"organization_slug": org.slug, "token": invite.token},
        )
        response = api_client.post(url)
        assert response.status_code == http_status.HTTP_400_BAD_REQUEST

    def test_accept_invite_wrong_email(self, api_client):
        org = OrganizationFactory()
        invite = OrganizationInviteFactory(
            organization=org,
            email="someone@example.com",
            expires_at=tz.now() + timedelta(days=7),
        )
        wrong_user = UserFactory(email="other@example.com")
        api_client.force_authenticate(user=wrong_user)
        url = reverse(
            "organizations:invite-accept",
            kwargs={"organization_slug": org.slug, "token": invite.token},
        )
        response = api_client.post(url)
        assert response.status_code == http_status.HTTP_403_FORBIDDEN
