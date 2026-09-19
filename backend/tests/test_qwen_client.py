import pytest
from app.agent.qwen_client import QwenClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_qwen_client_offline_simulation():
    client = QwenClient()
    assert client.model == settings.LOCAL_LLM_MODEL

    # Final response simulation
    res1 = await client.generate([{"role": "user", "content": "Hello FinPilot!"}])
    assert "FinPilot" in res1
    assert "final" in res1

    # Tool selection simulation: spending
    res2 = await client.generate([{"role": "user", "content": "How much did I spend on food?"}])
    assert "get_category_spending" in res2
    assert "tool" in res2

    # Tool selection simulation: purchase
    res3 = await client.generate([{"role": "user", "content": "Can I afford a 45000 laptop?"}])
    assert "analyze_purchase" in res3
    assert "45000" in res3 or "amount" in res3


@pytest.mark.asyncio
async def test_qwen_client_tool_explanation():
    client = QwenClient()
    messages = [
        {"role": "user", "content": "How much did I spend on food?"},
        {"role": "assistant", "content": '{"action": "tool", "tool": "get_category_spending", "arguments": {}}'},
        {"role": "user", "content": 'TOOL EXECUTION RESULT: {"category": "Food", "amount": 12500}'}
    ]
    res = await client.generate(messages)
    assert "final" in res
    assert "breakdown" in res.lower() or "financial" in res.lower()
