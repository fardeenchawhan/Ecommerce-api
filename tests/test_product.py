from unittest.mock import patch
from uuid import uuid4

from src.ai.schemas import ProductMetadataSchema


# -------------------------
# Helpers
# -------------------------

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


def register_normal_user(test_client):
    username = f"user_{uuid4().hex[:8]}"

    response = test_client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "username": username,
            "email": f"{username}@gmail.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 201

    return username


def login_user(test_client, username):
    response = test_client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "Password@123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def unique_product():
    uid = uuid4().hex[:8]

    return {
        "name": f"Nike Shoe {uid}",
        "description": "Running shoe",
        "price": "1999.99",
        "stock": 20,
        "brand": "Nike",
    }


# -------------------------
# AI + SKU Mocks
# -------------------------

def fake_metadata(*args, **kwargs):
    return ProductMetadataSchema(
        category="Electronics",
        category_id=1,
        tags=["phone", "smartphone"],
    )


def fake_sku(*args, **kwargs):
    return f"SKU-{uuid4().hex[:8]}"


@patch(
    "src.product.admin_service.generate_product_metadata",
    side_effect=fake_metadata,
)
@patch(
    "src.product.admin_service.generate_sku",
    side_effect=fake_sku,
)
def test_create_product_success(
    mock_sku,
    mock_ai,
    test_client,
):
    headers = login_admin(test_client)

    payload = unique_product()

    response = test_client.post(
        "/products",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["brand"] == payload["brand"]
    assert float(data["price"]) == float(payload["price"])
    assert data["stock"] == payload["stock"]
    assert data["category_id"] == 1
    assert data["sku"].startswith("SKU-")
    assert data["is_active"] is True



@patch(
    "src.product.admin_service.generate_product_metadata",
    side_effect=fake_metadata,
)
@patch(
    "src.product.admin_service.generate_sku",
    side_effect=fake_sku,
)
def test_duplicate_product(
    mock_sku,
    mock_ai,
    test_client,
):
    headers = login_admin(test_client)

    payload = unique_product()

    response = test_client.post(
        "/products",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201

    response = test_client.post(
        "/products",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 409
    print(response.json())
    assert response.json()["message"] == "Product already exists."



def test_normal_user_cannot_create_product(
    test_client,
):
    username = register_normal_user(test_client)

    headers = login_user(
        test_client,
        username,
    )

    payload = unique_product()

    response = test_client.post(
        "/products",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 403


@patch(
    "src.product.admin_service.generate_product_metadata",
    side_effect=fake_metadata,
)
@patch(
    "src.product.admin_service.generate_sku",
    side_effect=fake_sku,
)
def test_get_all_products(
    mock_sku,
    mock_ai,
    test_client,
):
    headers = login_admin(test_client)

    payload = unique_product()

    test_client.post(
        "/products",
        json=payload,
        headers=headers,
    )

    response = test_client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) >= 1


@patch(
    "src.product.admin_service.generate_product_metadata",
    side_effect=fake_metadata,
)
@patch(
    "src.product.admin_service.generate_sku",
    side_effect=fake_sku,
)
def test_get_one_product(
    mock_sku,
    mock_ai,
    test_client,
):
    headers = login_admin(test_client)

    payload = unique_product()

    response = test_client.post(
        "/products",
        json=payload,
        headers=headers,
    )

    product_id = response.json()["id"]

    response = test_client.get(
        f"/products/{product_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == payload["name"]


@patch(
    "src.product.admin_service.generate_product_metadata",
    side_effect=fake_metadata,
)
@patch(
    "src.product.admin_service.generate_sku",
    side_effect=fake_sku,
)
def test_update_product_success(
    mock_sku,
    mock_ai,
    test_client,
):
    headers = login_admin(test_client)

    payload = unique_product()

    response = test_client.post(
        "/products",
        json=payload,
        headers=headers,
    )

    product_id = response.json()["id"]

    response = test_client.put(
        f"/products/{product_id}",
        json={
            "price": 2500,
            "stock": 100,
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert float(data["price"]) == 2500
    assert data["stock"] == 100


@patch(
    "src.product.admin_service.generate_product_metadata",
    side_effect=fake_metadata,
)
@patch(
    "src.product.admin_service.generate_sku",
    side_effect=fake_sku,
)
def test_delete_product_success(
    mock_sku,
    mock_ai,
    test_client,
):
    headers = login_admin(test_client)

    payload = unique_product()

    response = test_client.post(
        "/products",
        json=payload,
        headers=headers,
    )

    product_id = response.json()["id"]

    response = test_client.delete(
        f"/products/{product_id}",
        headers=headers,
    )

    assert response.status_code == 204

    response = test_client.get(
        f"/products/{product_id}"
    )

    assert response.status_code == 404

def test_product_not_found(test_client):

    response = test_client.get(
        "/products/999999"
    )

    assert response.status_code == 404