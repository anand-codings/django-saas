"""Shared cryptographic utilities."""

import hashlib
import hmac
import secrets
import string


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure URL-safe token."""
    return secrets.token_urlsafe(length)


def generate_api_key(prefix: str = "sk") -> str:
    """Generate an API key like sk_live_abc123..."""
    token = secrets.token_hex(24)
    return f"{prefix}_{token}"


def hash_token(token: str) -> str:
    """Hash a token for secure storage. Use for API keys, invite tokens, etc."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_webhook_signature(payload: bytes, signature: str, secret: str, algorithm: str = "sha256") -> bool:
    """Verify an HMAC webhook signature."""
    expected = hmac.new(secret.encode(), payload, algorithm).hexdigest()
    return hmac.compare_digest(expected, signature)


def generate_short_code(length: int = 8) -> str:
    """Generate a short alphanumeric code (for invite codes, referral codes, etc.)."""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))
