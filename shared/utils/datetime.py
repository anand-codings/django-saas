"""Shared datetime utilities."""

from datetime import datetime, timedelta, timezone


def utc_now() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def days_from_now(days: int) -> datetime:
    """Return a UTC datetime N days from now."""
    return utc_now() + timedelta(days=days)


def is_expired(dt: datetime | None) -> bool:
    """Check if a datetime has passed."""
    if dt is None:
        return False
    return utc_now() > dt
