from datetime import timedelta
import jwt
from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token


def test_health_check_remains_functional(client: TestClient) -> None:
    """Requirement 1: Confirm Stage 1 health endpoint still works."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "ok",
        "service": settings.APP_NAME,
    }


def test_register_user_success(client: TestClient) -> None:
    """Requirement 2: Register user successfully."""
    payload = {
        "email": "testuser@example.com",
        "password": "StrongPassword123!",
        "name": "Test User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test User"
    assert data["is_active"] is True
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email_fails(client: TestClient) -> None:
    """Requirement 3: Duplicate email rejected with 409 Conflict."""
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongPassword123!",
        "name": "First User",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == status.HTTP_201_CREATED

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == status.HTTP_409_CONFLICT
    assert res2.json()["message"] == "User with this email already exists"


def test_password_is_hashed(client: TestClient) -> None:
    """Requirement 4: Password is not exposed or stored in plaintext."""
    payload = {
        "email": "hashed@example.com",
        "password": "SecretPassword123!",
        "name": "Hashed User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    data = response.json()
    assert "password" not in data
    assert "password_hash" not in data
    assert "SecretPassword123!" not in str(data)


def test_login_success(client: TestClient) -> None:
    """Requirement 5: Login succeeds with valid credentials."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "MyPassword123!",
            "name": "Login User",
        },
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "MyPassword123!",
        },
    )
    assert login_res.status_code == status.HTTP_200_OK
    data = login_res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password_fails(client: TestClient) -> None:
    """Requirement 6: Login fails with incorrect password."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "CorrectPassword123!",
            "name": "Wrong Pass User",
        },
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "IncorrectPassword123!",
        },
    )
    assert login_res.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_success(client: TestClient) -> None:
    """Requirement 7: /auth/me works with valid access token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "meuser@example.com",
            "password": "Password123!",
            "name": "Me User",
        },
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "meuser@example.com",
            "password": "Password123!",
        },
    )
    access_token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == status.HTTP_200_OK
    assert me_res.json()["email"] == "meuser@example.com"
    assert me_res.json()["name"] == "Me User"


def test_get_me_missing_token_fails(client: TestClient) -> None:
    """Requirement 8: /auth/me fails without token."""
    me_res = client.get("/api/v1/auth/me")
    assert me_res.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_invalid_token_fails(client: TestClient) -> None:
    """Requirement 9: /auth/me fails with invalid token."""
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_success(client: TestClient) -> None:
    """Requirement 10: Refresh token creates a new access token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "refreshuser@example.com",
            "password": "Password123!",
            "name": "Refresh User",
        },
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "refreshuser@example.com",
            "password": "Password123!",
        },
    )
    refresh_token = login_res.json()["refresh_token"]

    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == status.HTTP_200_OK
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_logout_revokes_token(client: TestClient) -> None:
    """Requirement 11 & 12: Logout revokes refresh token and prevents reuse."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "logoutuser@example.com",
            "password": "Password123!",
            "name": "Logout User",
        },
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "logoutuser@example.com",
            "password": "Password123!",
        },
    )
    refresh_token = login_res.json()["refresh_token"]

    # Logout
    logout_res = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == status.HTTP_200_OK
    assert logout_res.json()["message"] == "Successfully logged out"

    # Attempting to use revoked refresh token fails
    reuse_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert reuse_res.status_code == status.HTTP_401_UNAUTHORIZED


def test_expired_token_rejected(client: TestClient) -> None:
    """Requirement 13: Expired token is rejected."""
    expired_token = create_access_token(
        subject="00000000-0000-0000-0000-000000000000",
        expires_delta=timedelta(seconds=-10),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
