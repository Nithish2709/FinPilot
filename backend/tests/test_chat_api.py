import uuid
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    register_payload = {
        "email": "chat_user_a@finpilot.io",
        "password": "Password123!",
        "name": "Chat User A",
    }
    client.post("/api/v1/auth/register", json=register_payload)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "chat_user_a@finpilot.io", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user_b(client: TestClient) -> dict:
    register_payload = {
        "email": "chat_user_b@finpilot.io",
        "password": "Password123!",
        "name": "Chat User B",
    }
    client.post("/api/v1/auth/register", json=register_payload)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "chat_user_b@finpilot.io", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_conversation_lifecycle_and_user_isolation(
    client: TestClient, auth_headers: dict, auth_headers_user_b: dict
):
    # 1. Create conversation with title
    create_res = client.post(
        "/api/v1/conversations",
        headers=auth_headers,
        json={"title": "Monthly spending discussion"},
    )
    assert create_res.status_code == 201
    conv = create_res.json()
    conv_id = conv["id"]
    assert conv["title"] == "Monthly spending discussion"
    assert conv["archived"] is False

    # 2. List conversations
    list_res = client.get("/api/v1/conversations", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    assert list_res.json()["items"][0]["id"] == conv_id

    # 3. User B cannot see User A's conversation in list
    b_list = client.get("/api/v1/conversations", headers=auth_headers_user_b)
    assert b_list.status_code == 200
    assert b_list.json()["total"] == 0

    # User B cannot access User A's conversation directly -> 404
    b_get = client.get(f"/api/v1/conversations/{conv_id}", headers=auth_headers_user_b)
    assert b_get.status_code == 404

    # 4. User A updates conversation title & archives it
    patch_res = client.patch(
        f"/api/v1/conversations/{conv_id}",
        headers=auth_headers,
        json={"title": "Updated Title", "archived": True},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Updated Title"
    assert patch_res.json()["archived"] is True

    # User B cannot patch User A's conversation -> 404
    b_patch = client.patch(
        f"/api/v1/conversations/{conv_id}",
        headers=auth_headers_user_b,
        json={"title": "Hacked Title"},
    )
    assert b_patch.status_code == 404

    # 5. User B cannot delete User A's conversation -> 404
    b_del = client.delete(f"/api/v1/conversations/{conv_id}", headers=auth_headers_user_b)
    assert b_del.status_code == 404

    # User A deletes conversation -> 200
    del_res = client.delete(f"/api/v1/conversations/{conv_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # Verify deleted
    assert client.get(f"/api/v1/conversations/{conv_id}", headers=auth_headers).status_code == 404


def test_messages_flow_and_sequence_ordering(
    client: TestClient, auth_headers: dict, auth_headers_user_b: dict
):
    # 1. Create a conversation
    conv = client.post(
        "/api/v1/conversations",
        headers=auth_headers,
        json={"title": "Budget query"},
    ).json()
    conv_id = conv["id"]

    # 2. Post first user message
    msg1_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers=auth_headers,
        json={"content": "How much did I spend on dining out?"},
    )
    assert msg1_res.status_code == 201
    asst_msg1 = msg1_res.json()
    assert asst_msg1["role"] == "ASSISTANT"
    assert asst_msg1["sequence_number"] == 2  # User was 1, Assistant is 2
    assert "Your financial assistant is being initialized" in asst_msg1["content"]

    # 3. Post second user message
    msg2_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers=auth_headers,
        json={"content": "And what about groceries?"},
    )
    assert msg2_res.status_code == 201
    asst_msg2 = msg2_res.json()
    assert asst_msg2["sequence_number"] == 4  # User was 3, Assistant is 4

    # 4. Fetch message history
    hist_res = client.get(
        f"/api/v1/conversations/{conv_id}/messages",
        headers=auth_headers,
    )
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert history["total"] == 4
    # Check strict chronological sequence
    seqs = [m["sequence_number"] for m in history["items"]]
    assert seqs == [1, 2, 3, 4]
    assert history["items"][0]["role"] == "USER"
    assert history["items"][1]["role"] == "ASSISTANT"
    assert history["items"][2]["role"] == "USER"
    assert history["items"][3]["role"] == "ASSISTANT"

    # 5. User B cannot access messages -> 404
    b_hist = client.get(
        f"/api/v1/conversations/{conv_id}/messages",
        headers=auth_headers_user_b,
    )
    assert b_hist.status_code == 404

    # User B cannot post message to User A's conversation -> 404
    b_post = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers=auth_headers_user_b,
        json={"content": "Malicious message"},
    )
    assert b_post.status_code == 404


def test_context_builder_and_length_validation(
    client: TestClient, auth_headers: dict
):
    conv = client.post(
        "/api/v1/conversations",
        headers=auth_headers,
        json={"title": "Context Test"},
    ).json()
    conv_id = conv["id"]

    # Add 2 user turns (4 messages total: seq 1, 2, 3, 4)
    client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers=auth_headers,
        json={"content": "First question"},
    )
    client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers=auth_headers,
        json={"content": "Second question"},
    )

    # Inspect context endpoint
    context_res = client.get(
        f"/api/v1/conversations/{conv_id}/context?limit=10",
        headers=auth_headers,
    )
    assert context_res.status_code == 200
    ctx = context_res.json()
    assert ctx["message_count"] == 4
    assert len(ctx["recent_messages"]) == 4
    # Confirm chronological order in context
    assert ctx["recent_messages"][0]["sequence_number"] == 1
    assert ctx["recent_messages"][3]["sequence_number"] == 4

    # Test message size limit validation (> 16,000 characters)
    huge_content = "A" * 16001
    large_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers=auth_headers,
        json={"content": huge_content},
    )
    assert large_res.status_code == 422
