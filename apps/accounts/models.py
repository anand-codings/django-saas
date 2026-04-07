"""User authentication, registration, login, password reset, email verification, and social login."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from shared.models.base import BaseModel


class User(AbstractUser):
    """Custom user model — email-based authentication."""

    email = models.EmailField("email address", unique=True)
    is_email_verified = models.BooleanField(
        "email verified",
        default=False,
        help_text="Designates whether the user has verified their email address.",
    )
    last_login_ip = models.GenericIPAddressField(
        "last login IP",
        null=True,
        blank=True,
        help_text="IP address recorded at the most recent login.",
    )
    date_of_birth = models.DateField(
        "date of birth",
        null=True,
        blank=True,
    )
    phone_number = models.CharField(
        "phone number",
        max_length=20,
        blank=True,
        default="",
        help_text="E.164 format preferred, e.g. +14155551234.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email


class UserProfile(BaseModel):
    """Core account data auto-created for every user via signal.

    This is intentionally separate from the profiles app, which handles
    public/social profile information. UserProfile stores internal account
    metadata such as preferences and onboarding state.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=150, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")
    timezone = models.CharField(
        max_length=63,
        blank=True,
        default="UTC",
        help_text="IANA timezone, e.g. America/New_York.",
    )
    locale = models.CharField(
        max_length=10,
        blank=True,
        default="en",
        help_text="BCP-47 language tag, e.g. en-US.",
    )
    onboarding_completed = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        verbose_name = "user profile"
        verbose_name_plural = "user profiles"

    def __str__(self):
        return f"Profile for {self.user.email}"
