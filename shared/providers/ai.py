"""Abstract AI/LLM provider interface.

Concrete implementations: OpenAI, Anthropic, AWS Bedrock, local models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Iterator


class AIRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class AIMessage:
    role: AIRole
    content: str


@dataclass
class AIUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class AIResponse:
    content: str
    model: str = ""
    usage: AIUsage | None = None
    finish_reason: str = ""
    raw_response: Any = None


@dataclass
class EmbeddingResult:
    embedding: list[float]
    model: str = ""
    usage: AIUsage | None = None


class AIProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def chat(self, messages: list[AIMessage], model: str = "", temperature: float = 0.7, max_tokens: int = 4096) -> AIResponse:
        ...

    @abstractmethod
    def stream_chat(self, messages: list[AIMessage], model: str = "", temperature: float = 0.7, max_tokens: int = 4096) -> Iterator[str]:
        ...

    @abstractmethod
    def embed(self, text: str | list[str], model: str = "") -> list[EmbeddingResult]:
        ...

    @abstractmethod
    def list_models(self) -> list[str]:
        ...

    @abstractmethod
    def check_health(self) -> bool:
        ...
