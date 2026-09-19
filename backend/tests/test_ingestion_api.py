import io
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.models.user import User


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    # Register and login user A
    register_payload = {
        "email": "user_a@finpilot.io",
        "password": "Password123!",
        "name": "User A",
    }
    res = client.post("/api/v1/auth/register", json=register_payload)
    assert res.status_code == 201

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "user_a@finpilot.io", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user_b(client: TestClient) -> dict:
    # Register and login user B for isolation testing
    register_payload = {
        "email": "user_b@finpilot.io",
        "password": "Password123!",
        "name": "User B",
    }
    res = client.post("/api/v1/auth/register", json=register_payload)
    assert res.status_code == 201

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "user_b@finpilot.io", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_unauthorized_upload(client: TestClient):
    csv_content = b"Date,Description,Amount\n2026-09-01,Test,100\n"
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 401


def test_unsupported_file_extension(client: TestClient, auth_headers: dict):
    exe_content = b"Binary executable content"
    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("malicious.exe", exe_content, "application/octet-stream")},
    )
    assert response.status_code == 400
    res_data = response.json()
    error_msg = res_data.get("message") or res_data.get("detail", "")
    assert "Unsupported file extension" in error_msg


def test_csv_upload_and_transactions_flow(client: TestClient, auth_headers: dict):
    # CSV with valid debit, valid credit, refund, duplicate, missing description, invalid amount
    csv_content = (
        "Date,Description,Debit,Credit,Ref\n"
        "2026-09-01,Swiggy Food,450.00,,UPI01\n"
        "2026-09-02,Salary Monthly,,80000.00,SAL01\n"
        "2026-09-03,Amazon Refund,,1999.00,REF01\n"
        "2026-09-04,Netflix Subscription,649.00,,NET01\n"
        "2026-09-04,Netflix Subscription,649.00,,NET01\n"
        "2026-09-05,,250.00,,INV01\n"
        "2026-09-06,Coffee Day,INVALID_AMT,,INV02\n"
    ).encode("utf-8")

    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("statement.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["total_records"] == 7
    assert data["successful_records"] == 4  # Swiggy, Salary, Amazon, first Netflix
    assert data["duplicate_records"] == 1   # second Netflix
    assert data["failed_records"] == 2      # missing desc, invalid amount

    doc_id = data["document_id"]

    # Check Document Status endpoint
    doc_res = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert doc_res.status_code == 200
    doc_data = doc_res.json()
    assert doc_data["document_id"] == doc_id
    assert doc_data["total_records"] == 7

    # Check Transactions API
    txns_res = client.get("/api/v1/transactions", headers=auth_headers)
    assert txns_res.status_code == 200
    txns_data = txns_res.json()
    assert txns_data["total"] == 7  # All records preserved with is_valid / is_duplicate flags

    # Check filters: transaction_type=REFUND
    refund_res = client.get("/api/v1/transactions?transaction_type=REFUND", headers=auth_headers)
    assert refund_res.status_code == 200
    refunds = refund_res.json()
    assert refunds["total"] == 1
    assert refunds["items"][0]["description"] == "Amazon Refund"
    assert refunds["items"][0]["transaction_type"] == "REFUND"
    assert Decimal(str(refunds["items"][0]["amount"])) == Decimal("1999.00")


def test_user_data_isolation(
    client: TestClient,
    auth_headers: dict,
    auth_headers_user_b: dict,
):
    # User A uploads document
    csv_content = "Date,Description,Amount\n2026-09-10,User A Secret Expense,500.00\n".encode("utf-8")
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("user_a_stmt.csv", csv_content, "text/csv")},
    )
    assert upload_res.status_code == 201
    doc_id_a = upload_res.json()["document_id"]

    # User B tries to access User A's document -> 404
    b_doc_res = client.get(f"/api/v1/documents/{doc_id_a}", headers=auth_headers_user_b)
    assert b_doc_res.status_code == 404

    # User B lists transactions -> should be 0 items, never see User A's transactions
    b_txns_res = client.get("/api/v1/transactions", headers=auth_headers_user_b)
    assert b_txns_res.status_code == 200
    assert b_txns_res.json()["total"] == 0
    assert len(b_txns_res.json()["items"]) == 0


def test_pagination(client: TestClient, auth_headers: dict):
    # Upload transactions
    lines = ["Date,Description,Amount"]
    for i in range(1, 11):
        lines.append(f"2026-09-{i:02d},Item {i},{i * 100}.00")
    csv_content = "\n".join(lines).encode("utf-8")

    client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("pagination_test.csv", csv_content, "text/csv")},
    )

    # Fetch page 1 (limit 3, offset 0)
    page1 = client.get("/api/v1/transactions?limit=3&offset=0", headers=auth_headers).json()
    assert len(page1["items"]) == 3
    assert page1["limit"] == 3
    assert page1["offset"] == 0

    # Fetch page 2 (limit 3, offset 3)
    page2 = client.get("/api/v1/transactions?limit=3&offset=3", headers=auth_headers).json()
    assert len(page2["items"]) == 3
    assert page2["offset"] == 3
    # Check distinct items
    assert page1["items"][0]["id"] != page2["items"][0]["id"]


def test_excel_upload(client: TestClient, auth_headers: dict):
    with open("tests/fixtures/sample_transactions.xlsx", "rb") as f:
        content = f.read()

    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("sample_transactions.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["total_records"] == 3
    assert data["successful_records"] == 3


def test_pdf_upload(client: TestClient, auth_headers: dict):
    with open("tests/fixtures/sample_statement.pdf", "rb") as f:
        content = f.read()

    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("sample_statement.pdf", content, "application/pdf")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["total_records"] >= 3


def test_file_size_validation(client: TestClient, auth_headers: dict, monkeypatch):
    from app.core.config import settings
    # Temporarily set upload limit to 100 bytes
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_BYTES", 100)
    large_content = b"Date,Description,Amount\n" + b"2026-09-01,Test Large Content Row,500.00\n" * 10

    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("large.csv", large_content, "text/csv")},
    )
    assert response.status_code == 413


def test_path_traversal_prevention(client: TestClient, auth_headers: dict):
    from app.services.ingestion.storage import StorageManager
    # 1. generate_storage_key generates a flat UUID filename irrespective of malicious path
    key = StorageManager.generate_storage_key("../../etc/passwd.csv")
    assert not key.startswith("..")
    assert "/" not in key and "\\" not in key

    # 2. get_file_path rejects traversal keys
    with pytest.raises(ValueError, match="Directory traversal attempt detected"):
        StorageManager.get_file_path("../malicious.csv")

