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
