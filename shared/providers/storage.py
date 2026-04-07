"""Abstract storage provider interface.

Concrete implementations: S3, GCS, Azure Blob, Local filesystem.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import IO, Any


@dataclass
class StorageObject:
    """Metadata about a stored object."""

    key: str
    size: int
    content_type: str
    last_modified: Any = None
    etag: str = ""
    metadata: dict[str, str] | None = None


class StorageProvider(ABC):
    """Abstract interface for file storage providers."""

    @abstractmethod
    def upload(self, key: str, file: IO[bytes], content_type: str = "", metadata: dict | None = None) -> str:
        """Upload a file. Returns the storage URL/key."""
        ...

    @abstractmethod
    def download(self, key: str) -> IO[bytes]:
        """Download a file by key."""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a file by key."""
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a file exists."""
        ...

    @abstractmethod
    def get_signed_url(self, key: str, expires_in: timedelta = timedelta(hours=1)) -> str:
        """Generate a pre-signed URL for temporary access."""
        ...

    @abstractmethod
    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list[StorageObject]:
        """List objects with an optional prefix filter."""
        ...

    @abstractmethod
    def get_metadata(self, key: str) -> StorageObject:
        """Get metadata for a stored object."""
        ...
