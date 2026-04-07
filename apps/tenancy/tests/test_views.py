from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from apps.tenancy.middleware import TenantMiddleware


class TenantHeaderUnauthenticatedTest(TestCase):
    """X-Tenant-ID header must be ignored for unauthenticated requests."""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(get_response=lambda r: MagicMock(status_code=200))

    def test_header_ignored_for_anonymous_user(self):
        """Unauthenticated requests must not resolve tenant from header."""
        request = self.factory.get("/api/v1/test/", HTTP_X_TENANT_ID="some-tenant-slug")
        # Simulate anonymous user
        request.user = MagicMock(is_authenticated=False)

        with patch.object(self.middleware, "_from_header") as mock_from_header, \
             patch.object(self.middleware, "_from_subdomain", return_value=None), \
             patch.object(self.middleware, "_from_path", return_value=None), \
             patch.object(self.middleware, "_from_user", return_value=None):
            self.middleware._resolve_tenant(request)
            mock_from_header.assert_not_called()

    def test_header_used_for_authenticated_user(self):
        """Authenticated requests should resolve tenant from header."""
        request = self.factory.get("/api/v1/test/", HTTP_X_TENANT_ID="some-tenant-slug")
        request.user = MagicMock(is_authenticated=True)

        with patch.object(self.middleware, "_from_header", return_value=MagicMock()) as mock_from_header:
            result = self.middleware._resolve_tenant(request)
            mock_from_header.assert_called_once()


class SuperuserCrossTenantAuditTest(TestCase):
    """Superuser cross-tenant access must be logged."""

    def test_superuser_access_logged(self):
        """_user_has_access must log when superuser accesses a tenant."""
        factory = RequestFactory()
        request = factory.get("/api/v1/test/")
        request.user = MagicMock(is_authenticated=True, is_superuser=True, pk=1, email="admin@example.com")

        tenant = MagicMock()
        tenant.id = "fake-uuid"
        tenant.slug = "acme"

        with patch("apps.tenancy.middleware.logger") as mock_logger:
            result = TenantMiddleware._user_has_access(request, tenant)
            self.assertTrue(result)
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            self.assertEqual(call_args[0][0], "superuser_cross_tenant_access")


# ---------------------------------------------------------------------------
# pytest-style API tests for TenantViewSet (using RequestFactory since
# tenancy URLs are not in config/urls.py)
# ---------------------------------------------------------------------------

import pytest
from rest_framework import status as http_status
from rest_framework.test import APIRequestFactory

from apps.tenancy.models import TenantMembership
from apps.tenancy.views import TenantViewSet
from conftest import TenantFactory, TenantMembershipFactory, UserFactory


class TestTenantViewSetAPI:
    def test_list_user_tenants(self):
        user = UserFactory()
        tenant = TenantFactory()
        TenantMembershipFactory(user=user, tenant=tenant)
        TenantFactory()  # user is not a member

        factory = APIRequestFactory()
        request = factory.get("/tenants/")
        request.user = user
        view = TenantViewSet.as_view({"get": "list"})
        response = view(request)
        response.render()
        assert response.status_code == http_status.HTTP_200_OK
        results = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        ids = [str(t["id"]) for t in results]
        assert str(tenant.pk) in ids

    def test_create_tenant(self):
        user = UserFactory()
        factory = APIRequestFactory()
        request = factory.post("/tenants/", {"name": "New Tenant", "slug": "new-tenant"})
        request.user = user
        view = TenantViewSet.as_view({"post": "create"})
        response = view(request)
        assert response.status_code == http_status.HTTP_201_CREATED
        assert TenantMembership.objects.filter(user=user, role="owner").exists()

    def test_soft_delete(self):
        user = UserFactory()
        tenant = TenantFactory(status="active")
        TenantMembershipFactory(user=user, tenant=tenant)

        factory = APIRequestFactory()
        request = factory.delete(f"/tenants/{tenant.pk}/")
        request.user = user
        view = TenantViewSet.as_view({"delete": "destroy"})
        response = view(request, id=tenant.pk)
        assert response.status_code == http_status.HTTP_204_NO_CONTENT
        tenant.refresh_from_db()
        assert tenant.status == "inactive"

    def test_members_action(self):
        user = UserFactory()
        tenant = TenantFactory()
        TenantMembershipFactory(user=user, tenant=tenant)

        factory = APIRequestFactory()
        request = factory.get(f"/tenants/{tenant.pk}/members/")
        request.user = user
        view = TenantViewSet.as_view({"get": "members"})
        response = view(request, id=tenant.pk)
        assert response.status_code == http_status.HTTP_200_OK
        assert len(response.data) == 1
