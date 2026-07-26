import uuid


def register_user(test_client):
    payload = {
        "name": "User",
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"{uuid.uuid4().hex[:8]}@test.com",
        "password": "Password@123",
    }

    response = test_client.post("/auth/register", json=payload)
    assert response.status_code == 201

    login = test_client.post(
        "/auth/login",
        json={
            "username": payload["username"],
            "password": payload["password"],
        },
    )

    token = login.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def login_admin(test_client):
    response = test_client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Admin@123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def unique_category():
    return {
        "name": f"Category_{uuid.uuid4().hex[:8]}"
    }


def test_create_category_success(test_client):
    headers = login_admin(test_client)

    payload = unique_category()

    response = test_client.post(
        "/categories",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["product_count"] == 0
    assert "id" in data


def test_create_duplicate_category(test_client):
    headers = login_admin(test_client)

    payload = unique_category()

    response = test_client.post(
        "/categories",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201

    response = test_client.post(
        "/categories",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["status"] == 400
    assert data["message"] == "Category already exists"


def test_get_all_categories(test_client):
    response = test_client.get("/categories")

    assert response.status_code == 200

    assert isinstance(response.json(), list)


def test_get_single_category(test_client):
    headers = login_admin(test_client)

    payload = unique_category()

    created = test_client.post(
        "/categories",
        json=payload,
        headers=headers,
    ).json()

    response = test_client.get(
        f"/categories/{created['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == created["id"]
    assert data["name"] == payload["name"]


def test_update_category_success(test_client):
    headers = login_admin(test_client)

    payload = unique_category()

    created = test_client.post(
        "/categories",
        json=payload,
        headers=headers,
    ).json()

    body = {
        "name": f"Updated_{uuid.uuid4().hex[:6]}"
    }

    response = test_client.put(
        f"/categories/{created['id']}",
        json=body,
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == body["name"]


def test_delete_category_success(test_client):
    headers = login_admin(test_client)

    payload = unique_category()

    created = test_client.post(
        "/categories",
        json=payload,
        headers=headers,
    ).json()

    response = test_client.delete(
        f"/categories/{created['id']}",
        headers=headers,
    )

    assert response.status_code == 204

    response = test_client.get(
        f"/categories/{created['id']}"
    )

    assert response.status_code == 404


def test_normal_user_cannot_create_category(test_client):
    headers = register_user(test_client)

    response = test_client.post(
        "/categories",
        json=unique_category(),
        headers=headers,
    )

    assert response.status_code == 403


def test_normal_user_cannot_update_category(test_client):
    admin = login_admin(test_client)

    created = test_client.post(
        "/categories",
        json=unique_category(),
        headers=admin,
    ).json()

    user = register_user(test_client)

    response = test_client.put(
        f"/categories/{created['id']}",
        json={"name": "Updated"},
        headers=user,
    )

    assert response.status_code == 403


def test_normal_user_cannot_delete_category(test_client):
    admin = login_admin(test_client)

    created = test_client.post(
        "/categories",
        json=unique_category(),
        headers=admin,
    ).json()

    user = register_user(test_client)

    response = test_client.delete(
        f"/categories/{created['id']}",
        headers=user,
    )

    assert response.status_code == 403