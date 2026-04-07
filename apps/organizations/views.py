"""DRF viewsets for the organizations app."""

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from shared.types.enums import MembershipRole

from .models import InviteStatus, Membership, Organization, OrganizationInvite
from .serializers import (
    InviteCreateSerializer,
    MembershipSerializer,
    MembershipUpdateSerializer,
    OrganizationCreateSerializer,
    OrganizationInviteSerializer,
    OrganizationSerializer,
)


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


class IsOrgAdminOrOwner(permissions.BasePermission):
    """Allow only organization owners or admins."""

    def has_object_permission(self, request, view, obj):
        org = obj if isinstance(obj, Organization) else getattr(obj, "organization", None)
        if org is None:
            return False
        return Membership.objects.filter(
            user=request.user,
            organization=org,
            role__in=[MembershipRole.OWNER, MembershipRole.ADMIN],
            is_active=True,
        ).exists()


class IsOrgMember(permissions.BasePermission):
    """Allow any active member of the organization."""

    def has_object_permission(self, request, view, obj):
        org = obj if isinstance(obj, Organization) else getattr(obj, "organization", None)
        if org is None:
            return False
        return Membership.objects.filter(
            user=request.user,
            organization=org,
            is_active=True,
        ).exists()


# ---------------------------------------------------------------------------
# Organization ViewSet
# ---------------------------------------------------------------------------


class OrganizationViewSet(viewsets.ModelViewSet):
    """CRUD for organizations. Lists only the requesting user's organizations."""

    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "create":
            return OrganizationCreateSerializer
        return OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
        ).distinct()

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsOrgAdminOrOwner()]
        return super().get_permissions()


# ---------------------------------------------------------------------------
# Membership ViewSet
# ---------------------------------------------------------------------------


class MembershipViewSet(viewsets.ModelViewSet):
    """List, update, and remove memberships within an organization."""

    permission_classes = [permissions.IsAuthenticated, IsOrgMember]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action in ("partial_update", "update"):
            return MembershipUpdateSerializer
        return MembershipSerializer

    def get_queryset(self):
        return Membership.objects.filter(
            organization__slug=self.kwargs.get("organization_slug"),
        ).select_related("user", "organization")

    def get_permissions(self):
        if self.action in ("partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsOrgAdminOrOwner()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        # Prevent removing the last owner
        if instance.role == MembershipRole.OWNER:
            owner_count = Membership.objects.filter(
                organization=instance.organization,
                role=MembershipRole.OWNER,
                is_active=True,
            ).count()
            if owner_count <= 1:
                raise ValidationError({"detail": "Cannot remove the last owner."})
        instance.delete()


# ---------------------------------------------------------------------------
# Invite ViewSet
# ---------------------------------------------------------------------------


class InviteViewSet(viewsets.ModelViewSet):
    """Create, list, accept, and revoke organization invites."""

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return InviteCreateSerializer
        return OrganizationInviteSerializer

    def get_queryset(self):
        return OrganizationInvite.objects.filter(
            organization__slug=self.kwargs.get("organization_slug"),
        ).select_related("organization", "invited_by")

    def get_permissions(self):
        if self.action in ("create", "destroy", "list", "retrieve", "revoke"):
            return [permissions.IsAuthenticated(), IsOrgAdminOrOwner()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="accept/(?P<token>[^/.]+)")
    def accept(self, request, organization_slug=None, token=None):
        """Accept an invite by token. Creates a membership for the current user."""
        try:
            invite = OrganizationInvite.objects.get(
                token=token,
                organization__slug=organization_slug,
            )
        except OrganizationInvite.DoesNotExist:
            return Response(
                {"detail": "Invite not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not invite.is_acceptable:
            return Response(
                {"detail": "This invite is no longer valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.email.lower() != invite.email.lower():
            return Response(
                {"detail": "This invite was sent to a different email address."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if Membership.objects.filter(
            user=request.user, organization=invite.organization
        ).exists():
            return Response(
                {"detail": "You are already a member of this organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Membership.objects.create(
            user=request.user,
            organization=invite.organization,
            role=invite.role,
            invited_by=invite.invited_by,
        )

        invite.status = InviteStatus.ACCEPTED
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["status", "accepted_at", "updated_at"])

        return Response(
            {"detail": "Invite accepted."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="revoke")
    def revoke(self, request, organization_slug=None, pk=None):
        """Revoke a pending invite."""
        invite = self.get_object()
        if invite.status != InviteStatus.PENDING:
            return Response(
                {"detail": "Only pending invites can be revoked."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invite.status = InviteStatus.REVOKED
        invite.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Invite revoked."}, status=status.HTTP_200_OK)
