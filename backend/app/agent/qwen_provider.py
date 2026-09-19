import time
from typing import Dict, List, Optional

from app.agent.llm_provider import LLMProvider, LLMResult
from app.agent.qwen_client import QwenClient
from app.core.config import settings


class LocalQwenProvider(LLMProvider):
    """Primary local Qwen model provider."""

    def __init__(self, client: Optional[QwenClient] = None):
        self.client = client or QwenClient()

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def model_name(self) -> str:
        return self.client.model

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResult:
        start = time.time()
        content = await self.client.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency = round((time.time() - start) * 1000, 2)
        return LLMResult(
            content=content,
            provider=self.provider_name,
            model=self.model_name,
            latency_ms=latency,
            input_tokens=None,
            output_tokens=None,
        )
