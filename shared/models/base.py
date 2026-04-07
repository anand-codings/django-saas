"""Base model classes used across all domain slices.

Every app should inherit from one of these rather than raw models.Model.
This ensures consistent primary keys, timestamps, and tenant scoping.
"""

import uuid

from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    """Adds created_at / updated_at to any model."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class UUIDModel(models.Model):
    """Uses UUID as the primary key instead of auto-incrementing integer.

    Prevents enumeration attacks and makes IDs safe to expose in URLs/APIs.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampedModel):
    """Standard base for most models: UUID pk + timestamps.

    Usage:
        class MyModel(BaseModel):
            name = models.CharField(max_length=255)
    """

    class Meta(UUIDModel.Meta, TimestampedModel.Meta):
        abstract = True


class TenantManager(models.Manager):
    """QuerySet manager with tenant-scoped convenience methods."""

    def for_tenant(self, tenant_id):
        """Filter queryset to a specific tenant (accepts UUID or Tenant instance)."""
        return self.get_queryset().filter(tenant_id=tenant_id)

    def for_request(self, request):
        """Filter queryset using the tenant resolved by TenantMiddleware."""
        tenant = getattr(request, "tenant", None)
        if tenant is not None:
            return self.for_tenant(tenant.pk)
        # Fallback: raw tenant_id (for backwards compatibility).
        tenant_id = getattr(request, "tenant_id", None)
        if tenant_id is None:
            return self.none()
        return self.for_tenant(tenant_id)


class TenantAwareModel(BaseModel):
    """Base for models that belong to a tenant (organization).

    Adds a ``tenant`` FK and provides ``.for_tenant()`` queryset filtering.
    Used in shared-schema (row-level) multi-tenancy mode.

    Usage::

        class Invoice(TenantAwareModel):
            amount = models.DecimalField(...)
    """

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
        help_text="The organization/tenant this record belongs to.",
    )

    objects = models.Manager()
    tenant_objects = TenantManager()

    class Meta(BaseModel.Meta):
        abstract = True


class SoftDeleteModel(models.Model):
    """Mixin for soft-delete: marks records as deleted instead of removing them.

    Pairs with SoftDeleteManager to auto-exclude deleted records.
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records by default."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        return super().get_queryset()

    def only_deleted(self):
        return super().get_queryset().filter(is_deleted=True)
