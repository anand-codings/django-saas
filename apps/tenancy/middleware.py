"""Tenant middleware — resolves the current tenant from the request.

Supports both shared-schema (row-level) and schema-per-tenant modes
based on the TENANT_MODE setting.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from apps.tenancy.context import clear_current_tenant, set_current_tenant

logger = logging.getLogger(__name__)

# Pre-compiled pattern for extracting tenant slug from URL path, e.g. /t/<slug>/...
_PATH_TENANT_RE = re.compile(r"^/t/(?P<slug>[a-zA-Z0-9_-]+)/")


class TenantMiddleware:
    """Resolve and attach the current tenant to every request.

    Resolution order (first match wins):
        1. ``X-Tenant-ID`` header  (UUID or slug)
        2. Subdomain  (``acme.example.com`` -> slug ``acme``)
        3. URL path prefix  (``/t/acme/...`` -> slug ``acme``)
        4. Authenticated user's default tenant

    In schema-per-tenant mode the middleware also switches the PostgreSQL
    ``search_path`` and resets it after the response.
    """

    TENANT_HEADER = "X-Tenant-ID"
    # Paths that should never require a tenant (health-checks, auth, etc.).
    EXEMPT_PATHS: tuple[str, ...] = (
        "/health",
        "/readiness",
        "/api/auth/",
        "/admin/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Skip tenant resolution for exempt paths.
        if self._is_exempt(request.path):
            request.tenant = None  # type: ignore[attr-defined]
            request.tenant_id = None  # type: ignore[attr-defined]
            request.tenant_mode = getattr(settings, "TENANT_MODE", "shared")
            return self.get_response(request)

        tenant = self._resolve_tenant(request)

        # Verify authenticated users have membership in the resolved tenant.
        if tenant and not self._user_has_access(request, tenant):
            return JsonResponse(
                {"detail": "You do not have access to this tenant."},
                status=403,
            )

        # Attach to request.
        request.tenant = tenant  # type: ignore[attr-defined]
        request.tenant_id = str(tenant.id) if tenant else None  # type: ignore[attr-defined]
        request.tenant_mode = getattr(settings, "TENANT_MODE", "shared")

        # Store in context-var so non-request code can see it too.
        set_current_tenant(tenant)

        # Schema-per-tenant: switch search_path.
        if tenant and request.tenant_mode == "schema":
            tenant.activate_schema()

        try:
            response = self.get_response(request)
        finally:
            # Always clean up.
            if tenant and request.tenant_mode == "schema":
                tenant.reset_schema()
            clear_current_tenant()

        return response

    # ------------------------------------------------------------------
    # Resolution helpers
    # ------------------------------------------------------------------

    def _resolve_tenant(self, request: HttpRequest):
        """Walk through resolution strategies and return the first match."""
        from apps.tenancy.models import Tenant

        user = getattr(request, "user", None)
        is_authenticated = user is not None and getattr(user, "is_authenticated", False)

        # 1. Explicit header (may be UUID or slug).
        # Only allow header-based resolution for authenticated requests to
        # prevent unauthenticated tenant enumeration.
        if is_authenticated:
            tenant = self._from_header(request)
            if tenant:
                return tenant

        # 2. Subdomain.
        tenant = self._from_subdomain(request)
        if tenant:
            return tenant

        # 3. URL path prefix.
        tenant = self._from_path(request)
        if tenant:
            return tenant

        # 4. Authenticated user's default tenant.
        tenant = self._from_user(request)
        if tenant:
            return tenant

        return None

    def _from_header(self, request: HttpRequest):
        from apps.tenancy.models import Tenant

        value = request.META.get(f"HTTP_{self.TENANT_HEADER.replace('-', '_').upper()}")
        if not value:
            return None
        return self._lookup(value)

    def _from_subdomain(self, request: HttpRequest):
        host = request.get_host().split(":")[0]
        parts = host.split(".")
        if len(parts) > 2:
            return self._lookup(parts[0])
        return None

    def _from_path(self, request: HttpRequest):
        match = _PATH_TENANT_RE.match(request.path)
        if match:
            return self._lookup(match.group("slug"))
        return None

    def _from_user(self, request: HttpRequest):
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return None
        from apps.tenancy.models import TenantMembership

        membership = (
            TenantMembership.objects.filter(user=user, is_default=True)
            .select_related("tenant")
            .first()
        )
        if membership:
            return membership.tenant
        return None

    # ------------------------------------------------------------------
    # Shared lookup
    # ------------------------------------------------------------------

    @staticmethod
    def _lookup(identifier: str):
        """Look up a Tenant by UUID, slug, or custom domain."""
        from apps.tenancy.models import Tenant

        # Try UUID first.
        import uuid

        try:
            uid = uuid.UUID(identifier)
            return Tenant.objects.filter(id=uid, status="active").first()
        except ValueError:
            pass

        # Fall back to slug, then domain.
        tenant = Tenant.objects.filter(slug=identifier, status="active").first()
        if tenant:
            return tenant
        return Tenant.objects.filter(domain=identifier, status="active").first()

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    @staticmethod
    def _user_has_access(request: HttpRequest, tenant) -> bool:
        """Check that the authenticated user is a member of the resolved tenant.

        Unauthenticated requests are allowed through (auth is enforced by views).
        Staff/superusers bypass the check but access is logged for audit.
        """
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return True  # Let view-level auth handle unauthenticated requests.
        if getattr(user, "is_superuser", False):
            logger.info(
                "superuser_cross_tenant_access",
                extra={
                    "user_id": user.pk,
                    "user_email": getattr(user, "email", ""),
                    "tenant_id": str(tenant.id),
                    "tenant_slug": tenant.slug,
                    "path": request.path,
                    "method": request.method,
                },
            )
            return True
        from apps.tenancy.models import TenantMembership

        return TenantMembership.objects.filter(
            user=user, tenant=tenant
        ).exists()

    def _is_exempt(self, path: str) -> bool:
        return any(path.startswith(p) for p in self.EXEMPT_PATHS)
