import json
from unittest.mock import AsyncMock, patch
import httpx
import pytest
from app.agent.ollama_provider import OllamaProvider
from app.core.config import settings


@pytest.mark.asyncio
async def test_ollama_provider_init_and_config():
    provider = OllamaProvider()
    assert provider.provider_name == "local"
    assert provider.model_name == settings.OLLAMA_MODEL
    assert provider.base_url == settings.OLLAMA_BASE_URL.rstrip("/")
    assert provider.timeout == settings.OLLAMA_TIMEOUT


@pytest.mark.asyncio
async def test_ollama_provider_offline_simulation():
    provider = OllamaProvider(base_url="http://invalid-host-99999:11434")

    # 1. Final answer simulation
    res1 = await provider.generate([{"role": "user", "content": "Hello FinPilot!"}])
    assert res1.provider == "local"
    assert res1.model == settings.OLLAMA_MODEL
    data1 = json.loads(res1.content)
    assert data1["action"] == "final"
    assert "FinPilot" in data1["answer"]

    # 2. Tool call simulation: spending
    res2 = await provider.generate([{"role": "user", "content": "How much did I spend on food?"}])
    data2 = json.loads(res2.content)
    assert data2["action"] == "tool"
    assert data2["tool"] == "get_category_spending"

    # 3. Tool call simulation: purchase
    res3 = await provider.generate([{"role": "user", "content": "Can I afford a 60000 laptop?"}])
    data3 = json.loads(res3.content)
    assert data3["action"] == "tool"
    assert data3["tool"] == "analyze_purchase"
    assert data3["arguments"]["amount"] == 60000.0


@pytest.mark.asyncio
async def test_ollama_provider_mock_http_success():
    provider = OllamaProvider()

    mock_ollama_response = {
        "model": "qwen2.5:1.5b-instruct-q4_K_M",
        "message": {
            "role": "assistant",
            "content": '{"action": "tool", "tool": "get_monthly_summary", "arguments": {"month": "2026-08"}}'
        },
        "prompt_eval_count": 42,
        "eval_count": 18
    }

    mock_response = httpx.Response(200, json=mock_ollama_response)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        res = await provider.generate([{"role": "user", "content": "How was my August spending?"}])
        assert res.provider == "local"
        assert res.model == "qwen2.5:1.5b-instruct-q4_K_M"
        assert res.input_tokens == 42
        assert res.output_tokens == 18
        data = json.loads(res.content)
        assert data["action"] == "tool"
        assert data["tool"] == "get_monthly_summary"


@pytest.mark.asyncio
async def test_ollama_provider_health_check():
    provider = OllamaProvider()

    # Mock /api/tags success with model present
    mock_tags_response = {
        "models": [
            {"name": "qwen2.5:1.5b-instruct-q4_K_M:latest", "model": "qwen2.5:1.5b-instruct-q4_K_M"}
        ]
    }
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = httpx.Response(200, json=mock_tags_response)
        health = await provider.check_health()
        assert health["status"] == "healthy"
        assert health["model"] == "qwen2.5:1.5b-instruct-q4_K_M"

    # Mock /api/tags with missing model
    mock_tags_missing = {"models": [{"name": "llama3:latest"}]}
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = httpx.Response(200, json=mock_tags_missing)
        health = await provider.check_health()
        assert health["status"] == "missing_model"
        assert "ollama pull" in health["error"]
