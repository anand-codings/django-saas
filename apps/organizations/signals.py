"""Signals for the organizations app.

Auto-creates an OWNER membership when a new Organization is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from shared.types.enums import MembershipRole

from .models import Membership, Organization


@receiver(post_save, sender=Organization)
def create_owner_membership(sender, instance, created, **kwargs):
    """When an organization is created, add the owner as an OWNER member."""
    if created:
        Membership.objects.get_or_create(
            user=instance.owner,
            organization=instance,
            defaults={
                "role": MembershipRole.OWNER,
                "is_active": True,
            },
        )
