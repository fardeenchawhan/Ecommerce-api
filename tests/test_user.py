import uuid


def register_and_login(test_client):
    """
    Creates a fresh user and returns its JWT token + payload.
    """
    payload = {
        "name": "Fardin",
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"{uuid.uuid4().hex[:8]}@test.com",
        "password": "Password@123",
    }

    register = test_client.post("/auth/register", json=payload)
    assert register.status_code == 201

    login = test_client.post(
        "/auth/login",
        json={
            "username": payload["username"],
            "password": payload["password"],
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    return headers, payload


def test_get_current_user(test_client):
    headers, payload = register_and_login(test_client)

    response = test_client.get(
        "/users/me",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["is_admin"] is False
    assert "id" in data


def test_get_current_user_unauthorized(test_client):
    response = test_client.get("/users/me")

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 401


def test_update_profile_success(test_client):
    headers, payload = register_and_login(test_client)

    body = {
        "name": "Updated User",
        "username": f"updated_{uuid.uuid4().hex[:6]}",
        "email": f"{uuid.uuid4().hex[:6]}@test.com",
    }

    response = test_client.patch(
        "/users/me",
        json=body,
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == body["name"]
    assert data["username"] == body["username"]
    assert data["email"] == body["email"]


def test_update_duplicate_username(test_client):
    headers1, _ = register_and_login(test_client)
    headers2, payload2 = register_and_login(test_client)

    body = {
        "username": payload2["username"]
    }

    response = test_client.patch(
        "/users/me",
        json=body,
        headers=headers1,
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 400
    assert data["message"] == "Username already exists."


def test_update_duplicate_email(test_client):
    headers1, _ = register_and_login(test_client)
    headers2, payload2 = register_and_login(test_client)

    body = {
        "email": payload2["email"]
    }

    response = test_client.patch(
        "/users/me",
        json=body,
        headers=headers1,
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 400
    assert data["message"] == "Email already exists."


def test_change_password_success(test_client):
    headers, payload = register_and_login(test_client)

    response = test_client.patch(
        "/users/change-password",
        headers=headers,
        json={
            "current_password": payload["password"],
            "new_password": "NewPassword@123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Password changed successfully."

    login = test_client.post(
        "/auth/login",
        json={
            "username": payload["username"],
            "password": "NewPassword@123",
        },
    )

    assert login.status_code == 200


def test_change_password_wrong_current_password(test_client):
    headers, payload = register_and_login(test_client)

    response = test_client.patch(
        "/users/change-password",
        headers=headers,
        json={
            "current_password": "WrongPassword123",
            "new_password": "NewPassword@123",
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 400
    assert data["message"] == "Current password is incorrect."


def test_change_password_same_password(test_client):
    headers, payload = register_and_login(test_client)

    response = test_client.patch(
        "/users/change-password",
        headers=headers,
        json={
            "current_password": payload["password"],
            "new_password": payload["password"],
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 400
    assert (
        data["message"]
        == "New password must be different from the current password."
    )


def test_change_password_unauthorized(test_client):
    response = test_client.patch(
        "/users/change-password",
        json={
            "current_password": "Password@123",
            "new_password": "NewPassword@123",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 401