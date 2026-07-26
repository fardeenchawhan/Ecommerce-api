import uuid


def unique_user():
    uid = uuid.uuid4().hex[:8]
    return {
        "name": "Fardin",
        "username": f"user_{uid}",
        "email": f"user_{uid}@test.com",
        "password": "Password@123",
    }


def test_register_user_success(test_client):
    payload = unique_user()

    response = test_client.post("/auth/register", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["name"] == payload["name"]
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "hash_password" not in data


def test_register_duplicate_username(test_client):
    payload = unique_user()

    response = test_client.post("/auth/register", json=payload)
    assert response.status_code == 201

    duplicate = payload.copy()
    duplicate["email"] = f"{uuid.uuid4().hex[:8]}@test.com"

    response = test_client.post("/auth/register", json=duplicate)

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 400
    assert data["message"] == "Username already exists"


def test_register_duplicate_email(test_client):
    payload = unique_user()

    response = test_client.post("/auth/register", json=payload)
    assert response.status_code == 201

    duplicate = payload.copy()
    duplicate["username"] = f"user_{uuid.uuid4().hex[:8]}"

    response = test_client.post("/auth/register", json=duplicate)

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 400
    assert data["message"] == "Email already exists"


def test_login_success(test_client):
    payload = unique_user()

    register = test_client.post("/auth/register", json=payload)
    assert register.status_code == 201

    login_payload = {
        "username": payload["username"],
        "password": payload["password"],
    }

    response = test_client.post("/auth/login", json=login_payload)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(test_client):
    payload = unique_user()

    register = test_client.post("/auth/register", json=payload)
    assert register.status_code == 201

    response = test_client.post(
        "/auth/login",
        json={
            "username": payload["username"],
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 401
    assert data["message"] == "Invalid username or password"

def test_login_nonexistent_user(test_client):
    response = test_client.post(
        "/auth/login",
        json={
            "username": "unknown_user",
            "password": "Password@123",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 401
    assert data["message"] == "Invalid username or password"