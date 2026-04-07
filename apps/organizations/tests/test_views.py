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
