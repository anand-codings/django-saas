"""Shared enums and constants used across multiple domain slices."""

from django.db import models


class Status(models.TextChoices):
    """Generic status for records with a lifecycle."""

    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ARCHIVED = "archived", "Archived"
    DELETED = "deleted", "Deleted"


class MembershipRole(models.TextChoices):
    """Roles within an organization."""

    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    MEMBER = "member", "Member"
    VIEWER = "viewer", "Viewer"
    BILLING = "billing", "Billing"


class Currency(models.TextChoices):
    """Supported currencies."""

    USD = "usd", "US Dollar"
    EUR = "eur", "Euro"
    GBP = "gbp", "British Pound"
    CAD = "cad", "Canadian Dollar"
    AUD = "aud", "Australian Dollar"
    JPY = "jpy", "Japanese Yen"
    INR = "inr", "Indian Rupee"
    BRL = "brl", "Brazilian Real"


class Interval(models.TextChoices):
    """Billing / scheduling intervals."""

    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"
    YEARLY = "yearly", "Yearly"
    ONE_TIME = "one_time", "One-time"
