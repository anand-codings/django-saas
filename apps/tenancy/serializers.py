"""REST-framework serializers for the tenancy app."""

from rest_framework import serializers

from apps.tenancy.models import Tenant, TenantMembership, TenantStatus


class TenantSerializer(serializers.ModelSerializer):
    """Read serializer — exposes all safe fields of a tenant."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Tenant
        fields = [
            "id",
            "name",
            "slug",
            "domain",
            "schema_name",
            "settings",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TenantCreateSerializer(serializers.ModelSerializer):
    """Write serializer used when creating a new tenant.

    Only accepts the minimal set of fields needed; everything else gets
    sensible defaults.
    """

    class Meta:
        model = Tenant
        fields = [
            "name",
            "slug",
            "domain",
            "schema_name",
            "settings",
        ]
        extra_kwargs = {
            "domain": {"required": False},
            "schema_name": {"required": False},
            "settings": {"required": False},
        }

    def validate_slug(self, value: str) -> str:
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A tenant with this slug already exists.")
        return value


class TenantMembershipSerializer(serializers.ModelSerializer):
    """Serializer for tenant membership records."""

    tenant_name = serializers.CharField(source="tenant.name", read_only=True)

    class Meta:
        model = TenantMembership
        fields = [
            "id",
            "tenant",
            "tenant_name",
            "user",
            "role",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
