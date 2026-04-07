"""DRF viewsets for the tenancy app."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.tenancy.models import Tenant, TenantMembership
from apps.tenancy.serializers import (
    TenantCreateSerializer,
    TenantMembershipSerializer,
    TenantSerializer,
)


class TenantViewSet(viewsets.ModelViewSet):
    """CRUD operations on tenants.

    * ``GET    /tenants/``          — list tenants the current user belongs to
    * ``POST   /tenants/``          — create a new tenant
    * ``GET    /tenants/{id}/``     — retrieve a single tenant
    * ``PATCH  /tenants/{id}/``     — partial update
    * ``DELETE /tenants/{id}/``     — soft-remove (sets status to inactive)
    * ``GET    /tenants/current/``  — shortcut for the request's active tenant
    """

    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        """Scope to tenants the requesting user is a member of."""
        user = self.request.user
        tenant_ids = TenantMembership.objects.filter(user=user).values_list("tenant_id", flat=True)
        return Tenant.objects.filter(id__in=tenant_ids).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return TenantCreateSerializer
        return TenantSerializer

    def perform_create(self, serializer):
        """Create the tenant and add the requesting user as owner."""
        tenant = serializer.save()
        TenantMembership.objects.create(
            tenant=tenant,
            user=self.request.user,
            role="owner",
            is_default=not TenantMembership.objects.filter(user=self.request.user).exists(),
        )

    def perform_destroy(self, instance):
        """Soft-delete: mark the tenant as inactive rather than dropping it."""
        instance.status = "inactive"
        instance.save(update_fields=["status", "updated_at"])

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Return the tenant that is active on this request."""
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return Response(
                {"detail": "No active tenant on this request."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TenantSerializer(tenant)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="members")
    def members(self, request, id=None):
        """List memberships for a tenant."""
        tenant = self.get_object()
        memberships = TenantMembership.objects.filter(tenant=tenant).select_related("user")
        serializer = TenantMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
