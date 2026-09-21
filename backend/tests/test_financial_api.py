from datetime import date
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    # Register and login user A
    register_payload = {
        "email": "stage4_user_a@finpilot.io",
        "password": "Password123!",
        "name": "Stage 4 User A",
    }
    client.post("/api/v1/auth/register", json=register_payload)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "stage4_user_a@finpilot.io", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user_b(client: TestClient) -> dict:
    # Register and login user B
    register_payload = {
        "email": "stage4_user_b@finpilot.io",
        "password": "Password123!",
        "name": "Stage 4 User B",
    }
    client.post("/api/v1/auth/register", json=register_payload)
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "stage4_user_b@finpilot.io", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_budgets_crud_and_isolation(client: TestClient, auth_headers: dict, auth_headers_user_b: dict):
    # 1. User A creates a budget
    budget_payload = {
        "name": "Groceries & Dining",
        "category": "Food",
        "amount": "10000.00",
        "period": "monthly",
        "start_date": "2026-09-01",
    }
    res = client.post("/api/v1/budgets", headers=auth_headers, json=budget_payload)
    assert res.status_code == 201
    budget_data = res.json()
    budget_id = budget_data["id"]
    assert budget_data["status"] == "ON_TRACK"
    assert budget_data["remaining_amount"] == "10000.00"

    # 2. User A retrieves all budgets
    list_res = client.get("/api/v1/budgets", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 3. User B cannot see User A's budget
    b_list = client.get("/api/v1/budgets", headers=auth_headers_user_b)
    assert b_list.status_code == 200
    assert len(b_list.json()) == 0

    # User B cannot access User A's budget by ID
    b_get = client.get(f"/api/v1/budgets/{budget_id}", headers=auth_headers_user_b)
    assert b_get.status_code == 404

    # 4. User A updates budget
    up_res = client.put(
        f"/api/v1/budgets/{budget_id}",
        headers=auth_headers,
        json={"amount": "12000.00"},
    )
    assert up_res.status_code == 200
    assert up_res.json()["amount"] == "12000.00"

    # 5. User A deletes budget
    del_res = client.delete(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # Verify deleted
    assert client.get(f"/api/v1/budgets/{budget_id}", headers=auth_headers).status_code == 404


def test_goals_crud_and_isolation(client: TestClient, auth_headers: dict, auth_headers_user_b: dict):
    # 1. User A creates a goal
    goal_payload = {
        "name": "Trip to Japan",
        "target_amount": "250000.00",
        "current_amount": "50000.00",
        "target_date": "2027-03-01",
    }
    res = client.post("/api/v1/goals", headers=auth_headers, json=goal_payload)
    assert res.status_code == 201
    goal_data = res.json()
    goal_id = goal_data["id"]
    assert goal_data["percentage_complete"] == "20.00"
    assert goal_data["remaining_amount"] == "200000.00"
    assert goal_data["is_completed"] is False

    # 2. User B cannot access User A's goal
    assert client.get(f"/api/v1/goals/{goal_id}", headers=auth_headers_user_b).status_code == 404
    b_goals = client.get("/api/v1/goals", headers=auth_headers_user_b).json()
    assert len(b_goals) == 0

    # 3. User A updates goal towards completion
    up_res = client.put(
        f"/api/v1/goals/{goal_id}",
        headers=auth_headers,
        json={"current_amount": "250000.00"},
    )
    assert up_res.status_code == 200
    assert up_res.json()["is_completed"] is True
    assert up_res.json()["remaining_amount"] == "0.00"

    # 4. User A deletes goal
    assert client.delete(f"/api/v1/goals/{goal_id}", headers=auth_headers).status_code == 204


def test_dashboard_and_analytics_flow(client: TestClient, auth_headers: dict):
    # 1. Upload sample statement with various expenses & income
    csv_content = (
        "Date,Description,Debit,Credit,Ref\n"
        "2026-09-01,Swiggy Lunch,450.00,,S01\n"
        "2026-09-02,Salary Payment,,90000.00,SAL01\n"
        "2026-09-03,Uber Cab Ride,350.00,,U01\n"
        "2026-09-04,Netflix Subscription,649.00,,N01\n"
        "2026-08-04,Netflix Subscription,649.00,,N02\n"
        "2026-07-04,Netflix Subscription,649.00,,N03\n"
    ).encode("utf-8")

    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("stmt.csv", csv_content, "text/csv")},
    )
    assert upload_res.status_code == 201

    # 2. Check Dashboard API
    dash_res = client.get("/api/v1/dashboard", headers=auth_headers)
    assert dash_res.status_code == 200
    dash = dash_res.json()
    assert "current_balance" in dash
    assert "monthly_income" in dash
    assert "monthly_expenses" in dash
    assert "data_quality" in dash

    # 3. Check Categories Analytics
    cat_res = client.get("/api/v1/analytics/categories", headers=auth_headers)
    assert cat_res.status_code == 200
    cats = cat_res.json()
    assert Decimal(str(cats["total_expenses"])) > Decimal("0.00")
    cat_names = [c["category"] for c in cats["categories"]]
    assert "Food" in cat_names or "Transport" in cat_names or "Entertainment" in cat_names

    # 4. Check Subscriptions API
    subs_res = client.get("/api/v1/subscriptions", headers=auth_headers)
    assert subs_res.status_code == 200
    subs = subs_res.json()
    assert len(subs) >= 1
    assert any("netflix" in s["merchant"].lower() for s in subs)

    # 5. Check Obligations API
    obs_res = client.get("/api/v1/obligations?days_ahead=60", headers=auth_headers)
    assert obs_res.status_code == 200
    assert "total_obligations" in obs_res.json()

    # 6. Check Purchase Scenario Analysis
    purchase_payload = {
        "amount": "45000.00",
        "purchase_date": "2026-10-01",
        "description": "Gaming Console",
        "safety_buffer": "15000.00",
    }
    purch_res = client.post("/api/v1/purchases/analyze", headers=auth_headers, json=purchase_payload)
    assert purch_res.status_code == 200
    purch = purch_res.json()
    assert "purchase_now" in purch["scenarios"]
    assert "wait" in purch["scenarios"]
    assert "disclaimer" in purch
    assert "recommendation" not in purch  # Pure math, no subjective advice
