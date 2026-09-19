import io
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def user_a_headers(client: TestClient) -> dict:
    client.post(
        "/api/v1/auth/register",
        json={"email": "alice_isolated@finpilot.io", "password": "Password123!", "name": "Alice"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "alice_isolated@finpilot.io", "password": "Password123!"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.fixture
def user_b_headers(client: TestClient) -> dict:
    client.post(
        "/api/v1/auth/register",
        json={"email": "bob_isolated@finpilot.io", "password": "Password123!", "name": "Bob"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "bob_isolated@finpilot.io", "password": "Password123!"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_user_document_chunks_isolation(client: TestClient, user_a_headers: dict, user_b_headers: dict):
    # Alice uploads a secret document
    alice_file = (
        "Date,Description,Amount,Type\n"
        "2026-08-01,Alice Secret Diamond Purchase,9999.00,DEBIT\n"
    )
    alice_doc = client.post(
        "/api/v1/documents/upload",
        headers=user_a_headers,
        files={"file": ("alice_statement.csv", io.BytesIO(alice_file.encode("utf-8")), "text/csv")},
    ).json()

    # Bob uploads a distinct document
    bob_file = (
        "Date,Description,Amount,Type\n"
        "2026-08-02,Bob Grocery Store Market,45.00,DEBIT\n"
    )
    bob_doc = client.post(
        "/api/v1/documents/upload",
        headers=user_b_headers,
        files={"file": ("bob_statement.csv", io.BytesIO(bob_file.encode("utf-8")), "text/csv")},
    ).json()

    # 1. Bob searches for "Diamond Purchase"
    bob_search = client.post(
        "/api/v1/documents/search",
        headers=user_b_headers,
        json={"query": "Alice Secret Diamond Purchase", "similarity_threshold": 0.0},
    )
    assert bob_search.status_code == 200
    bob_results = bob_search.json()["results"]

    # Bob MUST NOT see Alice's document chunks
    for res in bob_results:
        assert res["document_id"] != alice_doc["document_id"]
        assert "Diamond" not in res["content"]

    # 2. Alice searches for "Diamond Purchase"
    alice_search = client.post(
        "/api/v1/documents/search",
        headers=user_a_headers,
        json={"query": "Alice Secret Diamond Purchase", "similarity_threshold": 0.0},
    )
    assert alice_search.status_code == 200
    alice_results = alice_search.json()["results"]
    assert len(alice_results) > 0
    assert alice_results[0]["document_id"] == alice_doc["document_id"]
    assert "Diamond" in alice_results[0]["content"]

    # 3. Bob attempts to filter by Alice's document_id
    bob_target_alice = client.post(
        "/api/v1/documents/search",
        headers=user_b_headers,
        json={"query": "Diamond", "document_id": alice_doc["document_id"], "similarity_threshold": 0.0},
    )
    assert bob_target_alice.status_code == 200
    # Must return 0 results because document belongs to Alice
    assert bob_target_alice.json()["total_results"] == 0
