import uuid
import pytest
from fastapi.testclient import TestClient

from app.agent.agent_service import AgentService
from app.models.conversation import Conversation
from tests.conftest import TestingSessionLocal


@pytest.fixture
def agent_user_headers(client: TestClient) -> dict:
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "agent_tester@finpilot.io", "password": "Password123!", "name": "Agent Tester"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "agent_tester@finpilot.io", "password": "Password123!"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.asyncio
async def test_agent_service_process_message_with_tools(client: TestClient, agent_user_headers: dict):
    # 1. Create a conversation via API
    conv = client.post(
        "/api/v1/conversations",
        headers=agent_user_headers,
        json={"title": "Agent Spending Query"},
    ).json()
    conv_id = uuid.UUID(conv["id"])

    # 2. Extract user_id from me endpoint
    me = client.get("/api/v1/auth/me", headers=agent_user_headers).json()
    user_id = uuid.UUID(me["id"])

    # 3. Call AgentService directly
    async with TestingSessionLocal() as db:
        agent_svc = AgentService()
        result = await agent_svc.process_message(
            db=db,
            user_id=user_id,
            conversation_id=conv_id,
            user_message="How much did I spend on food this month?",
        )

        assert "answer" in result
        assert len(result["answer"]) > 0
        assert "local:" in result["model_used"]
        assert "metadata" in result
        assert result["metadata"]["tool_count"] >= 1
        assert result["metadata"]["tool_calls"][0]["tool"] == "get_category_spending"


def test_agent_chat_api_end_to_end(client: TestClient, agent_user_headers: dict):
    # Create conversation
    conv = client.post(
        "/api/v1/conversations",
        headers=agent_user_headers,
        json={"title": "E2E Chat with Agent"},
    ).json()
    conv_id = conv["id"]

    # Send message triggering agent loop
    post_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers=agent_user_headers,
        json={"content": "Can I afford a 30000 phone?"},
    )
    assert post_res.status_code == 201
    asst_msg = post_res.json()
    assert asst_msg["role"] == "ASSISTANT"
    assert asst_msg["sequence_number"] == 2
    assert "local:" in asst_msg["model_used"]
    assert len(asst_msg["content"]) > 0

    # Retrieve history to confirm persistence
    hist = client.get(f"/api/v1/conversations/{conv_id}/messages", headers=agent_user_headers).json()
    assert hist["total"] == 2
    assert hist["items"][0]["role"] == "USER"
    assert hist["items"][1]["role"] == "ASSISTANT"
    assert hist["items"][1]["content"] == asst_msg["content"]
