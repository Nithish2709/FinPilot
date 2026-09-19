from typing import Dict, List, Optional
import pytest
from app.agent.api_provider import ApiLLMProvider
from app.agent.circuit_breaker import CircuitBreaker, CircuitState
from app.agent.llm_provider import LLMProvider, LLMResult
from app.agent.llm_router import FallbackReason, LLMRouter


class MockFailingLocalProvider(LLMProvider):
    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def model_name(self) -> str:
        return "mock-failing-qwen"

    async def generate(self, messages: List[Dict[str, str]], temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> LLMResult:
        raise TimeoutError("Simulated local model timeout")


class MockMalformedLocalProvider(LLMProvider):
    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def model_name(self) -> str:
        return "mock-malformed-qwen"

    async def generate(self, messages: List[Dict[str, str]], temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> LLMResult:
        return LLMResult(
            content="NOT_VALID_JSON_STRING",
            provider=self.provider_name,
            model=self.model_name,
            latency_ms=10.0,
        )


@pytest.mark.asyncio
async def test_llm_router_normal_local_route():
    router = LLMRouter()
    res = await router.route_request([{"role": "user", "content": "Hello FinPilot!"}])
    assert res.fallback is False
    assert res.fallback_reason is None
    assert res.provider == "local"
    assert "final" in res.parsed_json.get("action", "") or "answer" in res.parsed_json


@pytest.mark.asyncio
async def test_llm_router_fallback_on_local_timeout():
    failing_local = MockFailingLocalProvider()
    api_provider = ApiLLMProvider()
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=10.0)

    router = LLMRouter(local_provider=failing_local, api_provider=api_provider, circuit_breaker=cb)
    res = await router.route_request([{"role": "user", "content": "How much did I spend on food?"}])

    assert res.fallback is True
    assert res.fallback_reason == FallbackReason.LOCAL_TIMEOUT
    assert res.provider == "api"
    assert "action" in res.parsed_json


@pytest.mark.asyncio
async def test_llm_router_fallback_on_malformed_json_retries():
    malformed_local = MockMalformedLocalProvider()
    api_provider = ApiLLMProvider()
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=10.0)

    router = LLMRouter(local_provider=malformed_local, api_provider=api_provider, circuit_breaker=cb)
    res = await router.route_request([{"role": "user", "content": "How much did I spend on dining?"}])

    assert res.fallback is True
    assert res.fallback_reason == FallbackReason.LOCAL_MAX_RETRIES
    assert res.provider == "api"


@pytest.mark.asyncio
async def test_llm_router_skips_local_when_circuit_open():
    failing_local = MockFailingLocalProvider()
    api_provider = ApiLLMProvider()
    cb = CircuitBreaker(failure_threshold=1, cooldown_seconds=60.0)
    cb.record_failure()  # Circuit now OPEN

    assert cb.state == CircuitState.OPEN

    router = LLMRouter(local_provider=failing_local, api_provider=api_provider, circuit_breaker=cb)
    res = await router.route_request([{"role": "user", "content": "Check subscriptions"}])

    assert res.fallback is True
    assert res.fallback_reason == FallbackReason.LOCAL_UNAVAILABLE
    assert res.provider == "api"
