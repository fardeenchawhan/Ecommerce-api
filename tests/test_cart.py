from uuid import uuid4

from sqlalchemy import select

from src.product.models import ProductModel
from src.utils.db import SessionLocal


# =====================================================
# Helpers
# =====================================================

def register_user(test_client):
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


def create_product(stock=10, active=True):
    db = SessionLocal()

    product = ProductModel(
        name=f"Product-{uuid4().hex[:6]}",
        description="Test Product",
        price=1000,
        stock=stock,
        brand="Apple",
        sku=f"SKU-{uuid4().hex[:8]}",
        category_id=1,
        is_active=active,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    product_id = product.id

    db.close()

    return product_id


def get_cart_item_id(user_id, product_id):
    from src.cart.models import CartItemModel

    db = SessionLocal()

    cart = db.execute(
        select(CartItemModel).where(
            CartItemModel.user_id == user_id,
            CartItemModel.product_id == product_id,
        )
    ).scalar_one()

    cart_id = cart.id

    db.close()

    return cart_id


def get_user(username):
    from src.user.models import Usermodel

    db = SessionLocal()

    user = db.execute(
        select(Usermodel).where(
            Usermodel.username == username
        )
    ).scalar_one()

    db.close()

    return user


# =====================================================
# Tests
# =====================================================

def test_add_to_cart_success(test_client):
    username = register_user(test_client)
    headers = login_user(test_client, username)

    product_id = create_product()

    response = test_client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 2,
        },
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["quantity"] == 2
    assert data["product"]["id"] == product_id


def test_add_same_product_twice(test_client):
    username = register_user(test_client)
    headers = login_user(test_client, username)

    product_id = create_product(stock=10)

    test_client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 2,
        },
        headers=headers,
    )

    response = test_client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 3,
        },
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["quantity"] == 5


def test_add_to_cart_insufficient_stock(test_client):
    username = register_user(test_client)
    headers = login_user(test_client, username)

    product_id = create_product(stock=2)

    response = test_client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 5,
        },
        headers=headers,
    )

    assert response.status_code == 400


def test_get_cart(test_client):
    username = register_user(test_client)
    headers = login_user(test_client, username)

    product_id = create_product()

    test_client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 2,
        },
        headers=headers,
    )

    response = test_client.get(
        "/cart",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 2
    assert len(data["items"]) == 1


def test_update_cart_quantity(test_client):
    username = register_user(test_client)
    headers = login_user(test_client, username)

    product_id = create_product(stock=20)

    test_client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 2,
        },
        headers=headers,
    )

    user = get_user(username)
    cart_id = get_cart_item_id(user.id, product_id)

    response = test_client.patch(
        f"/cart/{cart_id}",
        json={
            "quantity": 5,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 5


def test_remove_cart_item(test_client):
    username = register_user(test_client)
    headers = login_user(test_client, username)

    product_id = create_product()

    test_client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1,
        },
        headers=headers,
    )

    user = get_user(username)
    cart_id = get_cart_item_id(user.id, product_id)

    response = test_client.delete(
        f"/cart/{cart_id}",
        headers=headers,
    )

    assert response.status_code == 204


def test_clear_cart(test_client):
    username = register_user(test_client)
    headers = login_user(test_client, username)

    product1 = create_product()
    product2 = create_product()

    test_client.post(
        "/cart",
        json={
            "product_id": product1,
            "quantity": 1,
        },
        headers=headers,
    )

    test_client.post(
        "/cart",
        json={
            "product_id": product2,
            "quantity": 2,
        },
        headers=headers,
    )

    response = test_client.delete(
        "/cart",
        headers=headers,
    )

    assert response.status_code == 204

    response = test_client.get(
        "/cart",
        headers=headers,
    )

    assert response.json()["items"] == []


def test_add_inactive_product(test_client):
    username = register_user(test_client)
    headers = login_user(test_client, username)

    product_id = create_product(active=False)

    response = test_client.post(
        "/cart",
        json={
            "product_id": product_id,
            "quantity": 1,
        },
        headers=headers,
    )

    assert response.status_code == 404