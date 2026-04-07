"""Abstract email provider interface.

Concrete implementations: SES, SendGrid, Resend, Postmark, Mailgun, SMTP.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmailMessage:
    """Represents an email to be sent."""

    to: list[str]
    subject: str
    body_text: str = ""
    body_html: str = ""
    from_email: str = ""
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    reply_to: list[str] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)
    attachments: list[tuple[str, bytes, str]] = field(default_factory=list)  # (filename, content, mimetype)
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    template_id: str | None = None
    template_vars: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmailResult:
    """Result of an email send attempt."""

    success: bool
    message_id: str = ""
    provider: str = ""
    error: str = ""
    raw_response: Any = None


class EmailProvider(ABC):
    """Abstract interface for email sending providers."""

    @abstractmethod
    def send(self, message: EmailMessage) -> EmailResult:
        """Send a single email."""
        ...

    @abstractmethod
    def send_batch(self, messages: list[EmailMessage]) -> list[EmailResult]:
        """Send multiple emails in a batch."""
        ...

    @abstractmethod
    def check_health(self) -> bool:
        """Verify the provider connection is healthy."""
        ...
