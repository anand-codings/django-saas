"""Reusable view/viewset mixins for DRF and Ninja."""

from rest_framework import status
from rest_framework.response import Response


class TenantQuerySetMixin:
    """Automatically scope viewset querysets to the current tenant.

    Usage:
        class InvoiceViewSet(TenantQuerySetMixin, ModelViewSet):
            queryset = Invoice.objects.all()
    """

    def get_queryset(self):
        qs = super().get_queryset()
        tenant_id = getattr(self.request, "tenant_id", None)
        if tenant_id and hasattr(qs.model, "tenant_id"):
            return qs.filter(tenant_id=tenant_id)
        return qs

    def perform_create(self, serializer):
        """Inject tenant_id on creation."""
        tenant_id = getattr(self.request, "tenant_id", None)
        if tenant_id:
            serializer.save(tenant_id=tenant_id)
        else:
            serializer.save()


class MultiSerializerMixin:
    """Use different serializers for different actions.

    Usage:
        class UserViewSet(MultiSerializerMixin, ModelViewSet):
            serializer_class = UserSerializer
            serializer_classes = {
                "list": UserListSerializer,
                "create": UserCreateSerializer,
            }
    """

    serializer_classes: dict = {}

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)


class BulkActionMixin:
    """Add bulk create/update/delete to a viewset.

    Adds POST /bulk-create, PATCH /bulk-update, DELETE /bulk-delete endpoints.
    """

    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def bulk_delete(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"detail": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({"deleted": deleted_count}, status=status.HTTP_200_OK)
