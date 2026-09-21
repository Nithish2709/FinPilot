from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class LLMResult(BaseModel):
    """Normalized response payload across any LLM provider."""
    content: str
    provider: str
    model: str
    latency_ms: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    raw_metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract interface for any LLM provider."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of provider (e.g. 'local', 'api')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Configured model name identifier."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResult:
        """Executes model inference and returns standardized LLMResult."""
        pass
