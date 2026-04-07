"""Abstract payment provider interface.

Primary implementation: Stripe. Abstract for future providers (Paddle, Braintree, LemonSqueezy).

NOTE: The billing system now uses dj-stripe as its source of truth. Stripe API calls
are made directly in apps.billing.services rather than through this abstraction.
This interface is retained for potential future multi-provider support but is not
currently implemented or used by the billing app.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"


@dataclass
class PaymentIntent:
    """Represents a payment attempt."""

    provider_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    customer_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Subscription:
    """Represents a subscription."""

    provider_id: str
    plan_id: str
    status: SubscriptionStatus
    customer_id: str = ""
    current_period_start: Any = None
    current_period_end: Any = None
    cancel_at_period_end: bool = False
    trial_end: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Customer:
    """Represents a customer in the payment system."""

    provider_id: str
    email: str
    name: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class PaymentProvider(ABC):
    """Abstract interface for payment/subscription providers."""

    # Customers
    @abstractmethod
    def create_customer(self, email: str, name: str = "", metadata: dict | None = None) -> Customer:
        ...

    @abstractmethod
    def get_customer(self, customer_id: str) -> Customer:
        ...

    # Subscriptions
    @abstractmethod
    def create_subscription(self, customer_id: str, plan_id: str, trial_days: int = 0) -> Subscription:
        ...

    @abstractmethod
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Subscription:
        ...

    @abstractmethod
    def update_subscription(self, subscription_id: str, plan_id: str) -> Subscription:
        ...

    # Payments
    @abstractmethod
    def create_payment_intent(self, amount: Decimal, currency: str, customer_id: str) -> PaymentIntent:
        ...

    @abstractmethod
    def create_checkout_session(self, customer_id: str, plan_id: str, success_url: str, cancel_url: str) -> str:
        """Returns a checkout URL."""
        ...

    # Webhooks
    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> dict:
        """Verify and parse a webhook payload. Returns the event dict."""
        ...
