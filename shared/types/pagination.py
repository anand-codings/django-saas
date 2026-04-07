"""Shared pagination types for API responses."""

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class PaginatedResponse(Generic[T]):
    """Standard paginated response shape for all API endpoints."""

    count: int
    next: str | None
    previous: str | None
    results: list[T]
