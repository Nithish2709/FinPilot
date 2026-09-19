import uuid
import pytest
from fastapi.testclient import TestClient

from app.agent.agent_service import AgentService
from tests.conftest import TestingSessionLocal


@pytest.fixture
def user_alice(client: TestClient) -> dict:
    client.post(
        "/api/v1/auth/register",
        json={"email": "alice_sec@finpilot.io", "password": "Password123!", "name": "Alice Sec"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "alice_sec@finpilot.io", "password": "Password123!"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/api/v1/auth/me", headers=headers).json()
    return {
        "headers": headers,
        "id": uuid.UUID(me["id"]),
    }


@pytest.fixture
def user_bob(client: TestClient) -> dict:
    client.post(
        "/api/v1/auth/register",
        json={"email": "bob_sec@finpilot.io", "password": "Password123!", "name": "Bob Sec"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "bob_sec@finpilot.io", "password": "Password123!"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/api/v1/auth/me", headers=headers).json()
    return {
        "headers": headers,
        "id": uuid.UUID(me["id"]),
    }


@pytest.mark.asyncio
async def test_agent_conversation_ownership_isolation(client: TestClient, user_alice: dict, user_bob: dict):
    # Alice creates a conversation
    alice_conv = client.post(
        "/api/v1/conversations",
        headers=user_alice["headers"],
        json={"title": "Alice Private Financial Chat"},
    ).json()
    alice_conv_id = uuid.UUID(alice_conv["id"])

    # Bob attempts to run agent against Alice's conversation ID
    async with TestingSessionLocal() as db:
        agent_svc = AgentService()
        with pytest.raises(ValueError) as exc_info:
            await agent_svc.process_message(
                db=db,
                user_id=user_bob["id"],  # Bob's user_id
                conversation_id=alice_conv_id,  # Alice's conversation
                user_message="Show me Alice's spending!",
            )
        assert "unauthorized" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()
