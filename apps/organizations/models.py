"""Organization/workspace/team model with membership, roles, and org-level settings."""

from django.conf import settings as django_settings
from django.db import models
from django.utils import timezone

from shared.models.base import BaseModel
from shared.types.enums import MembershipRole, Status
from shared.utils.crypto import generate_token


class Organization(BaseModel):
    """A workspace / team / company that users belong to."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    logo = models.ImageField(upload_to="organizations/logos/", blank=True, null=True)
    description = models.TextField(blank=True, default="")
    website = models.URLField(blank=True, default="")
    settings = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    owner = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name


class Membership(BaseModel):
    """Links a user to an organization with a specific role."""

    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER,
    )
    is_active = models.BooleanField(default=True)
    invited_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_memberships",
    )
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta(BaseModel.Meta):
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.organization} ({self.role})"


class InviteStatus(models.TextChoices):
    """Status of an organization invite."""

    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REVOKED = "revoked", "Revoked"
    EXPIRED = "expired", "Expired"


class OrganizationInvite(BaseModel):
    """An invitation for a user (by email) to join an organization."""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invites",
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER,
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        default=generate_token,
    )
    invited_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_invites",
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=InviteStatus.choices,
        default=InviteStatus.PENDING,
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Organization Invite"
        verbose_name_plural = "Organization Invites"

    def __str__(self):
        return f"Invite {self.email} to {self.organization} ({self.status})"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_acceptable(self):
        return self.status == InviteStatus.PENDING and not self.is_expired
