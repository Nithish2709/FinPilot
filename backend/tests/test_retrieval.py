import io
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    register_payload = {
        "email": "rag_user_a@finpilot.io",
        "password": "Password123!",
        "name": "RAG User A",
    }
    client.post("/api/v1/auth/register", json=register_payload)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "rag_user_a@finpilot.io", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_b(client: TestClient) -> dict:
    register_payload = {
        "email": "rag_user_b@finpilot.io",
        "password": "Password123!",
        "name": "RAG User B",
    }
    client.post("/api/v1/auth/register", json=register_payload)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "rag_user_b@finpilot.io", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_document_search_lifecycle_and_top_k(client: TestClient, auth_headers: dict):
    # 1. Upload sample CSV statement
    csv_content = (
        "Date,Description,Amount,Type\n"
        "2026-08-01,Netflix subscription,15.99,DEBIT\n"
        "2026-08-05,Electricity utility bill,85.50,DEBIT\n"
        "2026-08-10,Salary deposit company,5000.00,CREDIT\n"
        "2026-08-15,Starbucks coffee roasters,5.75,DEBIT\n"
    )
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("statement.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["document_id"]

    # 2. Perform search with query
    search_res = client.post(
        "/api/v1/documents/search",
        headers=auth_headers,
        json={"query": "Netflix subscription", "top_k": 3, "similarity_threshold": 0.1},
    )
    assert search_res.status_code == 200
    res_data = search_res.json()
    assert res_data["total_results"] > 0
    assert len(res_data["results"]) <= 3

    first_chunk = res_data["results"][0]
    assert first_chunk["document_id"] == doc_id
    assert first_chunk["score"] > 0.1
    assert "Netflix" in first_chunk["content"] or "statement" in first_chunk["content"]

    # 3. Test filtering by specific document_id
    doc_search = client.post(
        "/api/v1/documents/search",
        headers=auth_headers,
        json={"query": "utility bill", "document_id": doc_id, "similarity_threshold": 0.0},
    )
    assert doc_search.status_code == 200
    assert doc_search.json()["total_results"] > 0


def test_search_unauthenticated_fails(client: TestClient):
    res = client.post(
        "/api/v1/documents/search",
        json={"query": "test without auth"},
    )
    assert res.status_code == 401


def test_search_empty_query_validation(client: TestClient, auth_headers: dict):
    res = client.post(
        "/api/v1/documents/search",
        headers=auth_headers,
        json={"query": ""},
    )
    assert res.status_code == 422
