"""Shared validators used across multiple apps."""

import re

from django.core.exceptions import ValidationError


def validate_slug(value: str) -> None:
    """Validate a URL-safe slug."""
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", value):
        raise ValidationError("Slug must contain only lowercase letters, numbers, and hyphens.")


def validate_hex_color(value: str) -> None:
    """Validate a hex color code."""
    if not re.match(r"^#[0-9a-fA-F]{6}$", value):
        raise ValidationError("Must be a valid hex color (e.g., #FF5733).")


def validate_phone_e164(value: str) -> None:
    """Validate E.164 phone number format."""
    if not re.match(r"^\+[1-9]\d{1,14}$", value):
        raise ValidationError("Phone number must be in E.164 format (e.g., +14155552671).")
