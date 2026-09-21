import enum
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

from app.agent.api_provider import ApiLLMProvider
from app.agent.circuit_breaker import CircuitBreaker, CircuitState
from app.agent.llm_provider import LLMProvider, LLMResult
from app.agent.ollama_provider import OllamaProvider
from app.agent.qwen_provider import LocalQwenProvider
from app.agent.tool_registry import ToolRegistry
from app.core.config import settings

logger = logging.getLogger(__name__)


class FallbackReason(str, enum.Enum):
    LOCAL_TIMEOUT = "LOCAL_TIMEOUT"
    LOCAL_UNAVAILABLE = "LOCAL_UNAVAILABLE"
    LOCAL_PARSE_ERROR = "LOCAL_PARSE_ERROR"
    LOCAL_INVALID_TOOL = "LOCAL_INVALID_TOOL"
    LOCAL_MAX_RETRIES = "LOCAL_MAX_RETRIES"
    LOCAL_INTERNAL_ERROR = "LOCAL_INTERNAL_ERROR"


class RouterResult(BaseModel):
    """Enriched output payload with provider metadata and reliability trace."""
    content: str
    parsed_json: Dict[str, Any]
    provider: str
    model: str
    fallback: bool
    fallback_reason: Optional[FallbackReason] = None
    latency_ms: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class LLMRouter:
    """
    Orchestrates Local-first routing with circuit breaking and controlled API fallback.
    """

    def __init__(
        self,
        local_provider: Optional[LLMProvider] = None,
        api_provider: Optional[ApiLLMProvider] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ):
        self.local_provider = local_provider or OllamaProvider()
        self.api_provider = api_provider or ApiLLMProvider()
        self.circuit_breaker = circuit_breaker or CircuitBreaker(
            failure_threshold=settings.CIRCUIT_FAILURE_THRESHOLD,
            cooldown_seconds=settings.CIRCUIT_COOLDOWN_SECONDS,
        )

    @staticmethod
    def _validate_response_json(content: str) -> Tuple[Optional[Dict[str, Any]], Optional[FallbackReason]]:
        """Parses and verifies structured tool or final schema."""
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if len(lines) >= 3 and lines[-1].startswith("```"):
                cleaned = "\n".join(lines[1:-1]).strip()

        try:
            data = json.loads(cleaned)
            if not isinstance(data, dict):
                return None, FallbackReason.LOCAL_PARSE_ERROR
        except Exception:
            return None, FallbackReason.LOCAL_PARSE_ERROR

        action = data.get("action")
        if action == "tool":
            tool_name = data.get("tool")
            if not tool_name:
                return None, FallbackReason.LOCAL_INVALID_TOOL
            try:
                ToolRegistry.get(tool_name)
            except KeyError:
                return None, FallbackReason.LOCAL_INVALID_TOOL
            return data, None

        elif action == "final" or "answer" in data:
            return data, None

        return None, FallbackReason.LOCAL_PARSE_ERROR

    async def route_request(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> RouterResult:
        """
        Attempts primary local Qwen first with retry capability.
        On failure or circuit OPEN, activates API LLM Fallback if enabled.
        """
        # 1. Check Circuit Breaker for Primary Provider
        if self.circuit_breaker.can_attempt_local():
            retries = settings.MAX_LOCAL_RETRIES
            last_reason = FallbackReason.LOCAL_INTERNAL_ERROR

            for attempt in range(retries + 1):
                try:
                    res: LLMResult = await self.local_provider.generate(
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    data, err_reason = self._validate_response_json(res.content)
                    if data is not None:
                        # Local request succeeded cleanly
                        self.circuit_breaker.record_success()
                        return RouterResult(
                            content=res.content,
                            parsed_json=data,
                            provider=res.provider,
                            model=res.model,
                            fallback=False,
                            fallback_reason=None,
                            latency_ms=res.latency_ms,
                            input_tokens=res.input_tokens,
                            output_tokens=res.output_tokens,
                        )
                    else:
                        last_reason = err_reason or FallbackReason.LOCAL_PARSE_ERROR
                except TimeoutError:
                    last_reason = FallbackReason.LOCAL_TIMEOUT
                except ConnectionError:
                    last_reason = FallbackReason.LOCAL_UNAVAILABLE
                except Exception:
                    last_reason = FallbackReason.LOCAL_INTERNAL_ERROR

            # All local attempts exhausted
            self.circuit_breaker.record_failure()
            fallback_reason = FallbackReason.LOCAL_MAX_RETRIES if last_reason == FallbackReason.LOCAL_PARSE_ERROR else last_reason
        else:
            logger.info("Circuit breaker is OPEN; routing directly to API fallback.")
            fallback_reason = FallbackReason.LOCAL_UNAVAILABLE

        # 2. Trigger API Fallback
        if not settings.API_FALLBACK_ENABLED:
            raise RuntimeError(f"Local LLM failure ({fallback_reason.value}) and API fallback is disabled.")

        logger.info(f"Activating API LLM fallback. Reason: {fallback_reason.value}")
        api_res: LLMResult = await self.api_provider.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        data, _ = self._validate_response_json(api_res.content)
        if data is None:
            # Fallback output safe wrapper
            data = {"action": "final", "answer": api_res.content}

        return RouterResult(
            content=api_res.content,
            parsed_json=data,
            provider=api_res.provider,
            model=api_res.model,
            fallback=True,
            fallback_reason=fallback_reason,
            latency_ms=api_res.latency_ms,
            input_tokens=api_res.input_tokens,
            output_tokens=api_res.output_tokens,
        )
