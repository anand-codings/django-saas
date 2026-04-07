"""Abstract SMS provider interface.

Concrete implementations: Twilio, Vonage, AWS SNS.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class SMSMessage:
    to: str
    body: str
    from_number: str = ""
    metadata: dict[str, Any] | None = None


@dataclass
class SMSResult:
    success: bool
    message_id: str = ""
    provider: str = ""
    error: str = ""


class SMSProvider(ABC):
    @abstractmethod
    def send(self, message: SMSMessage) -> SMSResult:
        ...

    @abstractmethod
    def check_health(self) -> bool:
        ...
