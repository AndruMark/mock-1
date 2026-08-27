from fastapi import status
from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    payload = {
        "email": "newuser@mock1.com",
        "password": "securepassword123",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient):
    payload = {
        "email": "duplicate@mock1.com",
        "password": "securepassword123",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "login@mock1.com", "password": "mypassword"},
    )

    response = client.post(
        "/auth/login",
        data={"username": "login@mock1.com", "password": "mypassword"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "fake@mock1.com", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
