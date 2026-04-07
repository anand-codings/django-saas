"""Abstract notification channel interface.

Each notification channel (email, push, SMS, in-app, Slack) implements this.
The notifications app orchestrates delivery across channels.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NotificationChannel(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"
    SLACK = "slack"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """A notification to deliver to a user."""

    recipient_id: str
    title: str
    body: str
    channels: list[NotificationChannel] = field(default_factory=lambda: [NotificationChannel.IN_APP])
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_url: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    category: str = ""


@dataclass
class DeliveryResult:
    channel: NotificationChannel
    success: bool
    error: str = ""


class NotificationChannelProvider(ABC):
    """Abstract interface for a single notification delivery channel."""

    channel: NotificationChannel

    @abstractmethod
    def deliver(self, notification: Notification) -> DeliveryResult:
        ...

    @abstractmethod
    def deliver_batch(self, notifications: list[Notification]) -> list[DeliveryResult]:
        ...
