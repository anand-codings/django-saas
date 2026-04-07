"""Django Ninja API endpoints for the organizations app."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError

from shared.types.enums import MembershipRole

from .models import InviteStatus, Membership, Organization, OrganizationInvite

router = Router(tags=["Organizations"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class OrganizationIn(Schema):
    name: str
    slug: str
    description: str = ""
    website: str = ""
    settings: dict = {}


class OrganizationOut(Schema):
    id: UUID
    name: str
    slug: str
    description: str
    website: str
    settings: dict
    status: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class OrganizationUpdateIn(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    settings: Optional[dict] = None


class MembershipOut(Schema):
    id: UUID
    user_id: UUID
    organization_id: UUID
    role: str
    is_active: bool
    joined_at: datetime
    created_at: datetime


class MembershipUpdateIn(Schema):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class InviteIn(Schema):
    email: str
    role: str = MembershipRole.MEMBER
    expires_at: datetime


class InviteOut(Schema):
    id: UUID
    organization_id: UUID
    email: str
    role: str
    token: str
    status: str
    expires_at: datetime
    created_at: datetime


class MessageOut(Schema):
    detail: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_org_for_member(slug: str, user) -> Organization:
    """Return organization if user is an active member, else 404."""
    org = get_object_or_404(Organization, slug=slug)
    if not Membership.objects.filter(user=user, organization=org, is_active=True).exists():
        raise HttpError(403, "You are not a member of this organization.")
    return org


def _require_admin_or_owner(org: Organization, user) -> Membership:
    """Return membership if user is admin/owner, else raise 403."""
    membership = Membership.objects.filter(
        user=user,
        organization=org,
        role__in=[MembershipRole.OWNER, MembershipRole.ADMIN],
        is_active=True,
    ).first()
    if not membership:
        raise HttpError(403, "Admin or owner role required.")
    return membership


# ---------------------------------------------------------------------------
# Organization endpoints
# ---------------------------------------------------------------------------


@router.get("/", response=List[OrganizationOut])
def list_organizations(request):
    """List organizations the current user belongs to."""
    orgs = Organization.objects.filter(
        memberships__user=request.auth,
        memberships__is_active=True,
    ).distinct()
    return list(orgs)


@router.post("/", response={201: OrganizationOut})
def create_organization(request, payload: OrganizationIn):
    """Create a new organization. The requesting user becomes the owner."""
    org = Organization.objects.create(owner=request.auth, **payload.dict())
    return 201, org


@router.get("/{slug}", response=OrganizationOut)
def get_organization(request, slug: str):
    """Retrieve a single organization by slug."""
    return _get_org_for_member(slug, request.auth)


@router.patch("/{slug}", response=OrganizationOut)
def update_organization(request, slug: str, payload: OrganizationUpdateIn):
    """Update organization details. Requires admin or owner role."""
    org = _get_org_for_member(slug, request.auth)
    _require_admin_or_owner(org, request.auth)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(org, field, value)
    org.save()
    return org


@router.delete("/{slug}", response={204: None})
def delete_organization(request, slug: str):
    """Delete an organization. Requires owner role."""
    org = _get_org_for_member(slug, request.auth)
    if not Membership.objects.filter(
        user=request.auth, organization=org, role=MembershipRole.OWNER, is_active=True
    ).exists():
        raise HttpError(403, "Only the owner can delete an organization.")
    org.delete()
    return 204, None


# ---------------------------------------------------------------------------
# Membership endpoints
# ---------------------------------------------------------------------------


@router.get("/{slug}/members", response=List[MembershipOut])
def list_members(request, slug: str):
    """List all members of an organization."""
    org = _get_org_for_member(slug, request.auth)
    return list(Membership.objects.filter(organization=org).select_related("user"))


@router.patch("/{slug}/members/{member_id}", response=MembershipOut)
def update_member(request, slug: str, member_id: UUID, payload: MembershipUpdateIn):
    """Update a member's role or active status. Requires admin/owner."""
    org = _get_org_for_member(slug, request.auth)
    _require_admin_or_owner(org, request.auth)
    membership = get_object_or_404(Membership, id=member_id, organization=org)

    data = payload.dict(exclude_unset=True)
    # Prevent demoting last owner
    if (
        "role" in data
        and membership.role == MembershipRole.OWNER
        and data["role"] != MembershipRole.OWNER
    ):
        if Membership.objects.filter(
            organization=org, role=MembershipRole.OWNER, is_active=True
        ).count() <= 1:
            raise HttpError(400, "Cannot change role of the last owner.")

    for field, value in data.items():
        setattr(membership, field, value)
    membership.save()
    return membership


@router.delete("/{slug}/members/{member_id}", response={204: None})
def remove_member(request, slug: str, member_id: UUID):
    """Remove a member from an organization. Requires admin/owner."""
    org = _get_org_for_member(slug, request.auth)
    _require_admin_or_owner(org, request.auth)
    membership = get_object_or_404(Membership, id=member_id, organization=org)

    if membership.role == MembershipRole.OWNER:
        if Membership.objects.filter(
            organization=org, role=MembershipRole.OWNER, is_active=True
        ).count() <= 1:
            raise HttpError(400, "Cannot remove the last owner.")

    membership.delete()
    return 204, None


# ---------------------------------------------------------------------------
# Invite endpoints
# ---------------------------------------------------------------------------


@router.get("/{slug}/invites", response=List[InviteOut])
def list_invites(request, slug: str):
    """List all invites for an organization."""
    org = _get_org_for_member(slug, request.auth)
    return list(OrganizationInvite.objects.filter(organization=org))


@router.post("/{slug}/invites", response={201: InviteOut})
def create_invite(request, slug: str, payload: InviteIn):
    """Create an invite. Requires admin/owner."""
    org = _get_org_for_member(slug, request.auth)
    _require_admin_or_owner(org, request.auth)

    if Membership.objects.filter(
        organization=org, user__email=payload.email, is_active=True
    ).exists():
        raise HttpError(400, "This user is already a member.")

    invite = OrganizationInvite.objects.create(
        organization=org,
        invited_by=request.auth,
        **payload.dict(),
    )
    return 201, invite


@router.post("/{slug}/invites/accept/{token}", response=MessageOut)
def accept_invite(request, slug: str, token: str):
    """Accept an invite by token."""
    invite = get_object_or_404(
        OrganizationInvite, token=token, organization__slug=slug
    )
    if not invite.is_acceptable:
        raise HttpError(400, "This invite is no longer valid.")

    if Membership.objects.filter(
        user=request.auth, organization=invite.organization
    ).exists():
        raise HttpError(400, "You are already a member of this organization.")

    Membership.objects.create(
        user=request.auth,
        organization=invite.organization,
        role=invite.role,
        invited_by=invite.invited_by,
    )
    invite.status = InviteStatus.ACCEPTED
    invite.accepted_at = timezone.now()
    invite.save(update_fields=["status", "accepted_at", "updated_at"])
    return {"detail": "Invite accepted."}


@router.post("/{slug}/invites/{invite_id}/revoke", response=MessageOut)
def revoke_invite(request, slug: str, invite_id: UUID):
    """Revoke a pending invite. Requires admin/owner."""
    org = _get_org_for_member(slug, request.auth)
    _require_admin_or_owner(org, request.auth)
    invite = get_object_or_404(OrganizationInvite, id=invite_id, organization=org)

    if invite.status != InviteStatus.PENDING:
        raise HttpError(400, "Only pending invites can be revoked.")

    invite.status = InviteStatus.REVOKED
    invite.save(update_fields=["status", "updated_at"])
    return {"detail": "Invite revoked."}
