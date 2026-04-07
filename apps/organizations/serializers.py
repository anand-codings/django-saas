"""DRF serializers for the organizations app."""

from django.utils import timezone
from rest_framework import serializers

from shared.types.enums import MembershipRole

from .models import Membership, Organization, OrganizationInvite


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------


class OrganizationSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "description",
            "website",
            "settings",
            "status",
            "owner",
            "owner_email",
            "member_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "slug", "logo", "description", "website", "settings"]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


# ---------------------------------------------------------------------------
# Membership
# ---------------------------------------------------------------------------


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "user_email",
            "organization",
            "organization_name",
            "role",
            "is_active",
            "invited_by",
            "joined_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "organization",
            "invited_by",
            "joined_at",
            "created_at",
            "updated_at",
        ]


class MembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ["role", "is_active"]

    def validate_role(self, value):
        # Prevent demoting the last owner
        instance = self.instance
        if (
            instance
            and instance.role == MembershipRole.OWNER
            and value != MembershipRole.OWNER
        ):
            owner_count = Membership.objects.filter(
                organization=instance.organization,
                role=MembershipRole.OWNER,
                is_active=True,
            ).count()
            if owner_count <= 1:
                raise serializers.ValidationError(
                    "Cannot change role of the last owner."
                )
        return value


# ---------------------------------------------------------------------------
# Organization Invite
# ---------------------------------------------------------------------------


class OrganizationInviteSerializer(serializers.ModelSerializer):
    invited_by_email = serializers.EmailField(
        source="invited_by.email", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = OrganizationInvite
        fields = [
            "id",
            "organization",
            "organization_name",
            "email",
            "role",
            "invited_by",
            "invited_by_email",
            "accepted_at",
            "expires_at",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "invited_by",
            "accepted_at",
            "status",
            "created_at",
            "updated_at",
        ]


class InviteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInvite
        fields = ["organization", "email", "role", "expires_at"]

    def validate_email(self, value):
        # Check for existing active membership
        org = self.initial_data.get("organization")
        if org and Membership.objects.filter(
            organization_id=org, user__email=value, is_active=True
        ).exists():
            raise serializers.ValidationError(
                "This user is already a member of the organization."
            )
        return value

    def validate_expires_at(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")
        return value

    def create(self, validated_data):
        validated_data["invited_by"] = self.context["request"].user
        return super().create(validated_data)
