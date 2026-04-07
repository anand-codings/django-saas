"""Multi-tenancy data isolation — supports both shared-schema (row-level) and schema-per-tenant."""

import logging

from django.conf import settings as django_settings
from django.db import connection, models

from shared.models.base import BaseModel, TenantAwareModel, TenantManager  # noqa: F401

logger = logging.getLogger(__name__)


class TenantStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"
    PENDING = "pending", "Pending Setup"


class Tenant(BaseModel):
    """An organization / workspace that owns data in this platform.

    In shared-schema mode the tenant is used for row-level filtering.
    In schema-per-tenant mode, ``schema_name`` determines the PostgreSQL
    search_path that gets set by TenantMiddleware.
    """

    name = models.CharField(max_length=255, help_text="Display name for the tenant / organization.")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-safe identifier, also used as subdomain.",
    )
    domain = models.CharField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
        help_text="Optional custom domain mapped to this tenant.",
    )
    schema_name = models.CharField(
        max_length=63,
        blank=True,
        default="",
        help_text="PostgreSQL schema name (schema-per-tenant mode only).",
    )
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Arbitrary tenant-level configuration (feature flags, branding, limits, etc.).",
    )
    status = models.CharField(
        max_length=20,
        choices=TenantStatus.choices,
        default=TenantStatus.ACTIVE,
        db_index=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = "tenant"
        verbose_name_plural = "tenants"

    def __str__(self) -> str:
        return self.name

    # ------------------------------------------------------------------
    # Schema helpers
    # ------------------------------------------------------------------

    def activate_schema(self):
        """Set the PostgreSQL search_path to this tenant's schema.

        Only meaningful when TENANT_MODE == 'schema'.
        """
        if not self.schema_name:
            return
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO %s, public", [self.schema_name])

    def reset_schema(self):
        """Reset the PostgreSQL search_path back to public."""
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO public")


class TenantMembership(BaseModel):
    """Links a user to a tenant with a role.

    A user can belong to multiple tenants.  One of them is marked as the
    default (used when no explicit tenant header is sent).
    """

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenant_memberships",
    )
    role = models.CharField(
        max_length=50,
        default="member",
        help_text="Role within this tenant (e.g. owner, admin, member).",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="If True this is the user's default tenant.",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "tenant membership"
        verbose_name_plural = "tenant memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "user"],
                name="unique_tenant_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.tenant} ({self.role})"
