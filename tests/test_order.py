import uuid

from sqlalchemy import select

from src.cart.models import CartItemModel
from src.order.enums import OrderStatus
from src.order.models import OrderModel
from src.product.models import ProductModel
from src.utils.db import SessionLocal


# ==========================================================
# Helpers
# ==========================================================

def create_product(stock=10, active=True):
    db = SessionLocal()

    product = ProductModel(
        name=f"Phone-{uuid.uuid4().hex[:6]}",
        description="Test Product",
        price=1000,
        stock=stock,
        brand="Apple",
        sku=f"SKU-{uuid.uuid4().hex[:8]}",
        category_id=1,
        is_active=active,
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    db.close()

    return product.id


def add_product_to_cart(username, product_id, quantity=1):
    db = SessionLocal()

    from src.user.models import Usermodel

    user = db.execute(
        select(Usermodel).where(
            Usermodel.username == username
        )
    ).scalar_one()

    cart = CartItemModel(
        user_id=user.id,
        product_id=product_id,
        quantity=quantity,
    )

    db.add(cart)
    db.commit()
    db.close()


def register_and_login(test_client):
    username = f"user_{uuid.uuid4().hex[:8]}"

    register = test_client.post(
        "/auth/register",
        json={
            "name": "Test",
            "username": username,
            "email": f"{username}@gmail.com",
            "password": "Password@123",
        },
    )

    assert register.status_code == 201

    login = test_client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "Password@123",
        },
    )

    token = login.json()["access_token"]

    return username, {
        "Authorization": f"Bearer {token}"
    }


# ==========================================================
# Tests
# ==========================================================

def test_checkout_success(test_client):
    username, headers = register_and_login(test_client)

    product_id = create_product()

    add_product_to_cart(username, product_id)

    response = test_client.post(
        "/orders/checkout",
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "PENDING"
    assert data["total_items"] == 1
    assert float(data["total_amount"]) == 1000.0


def test_checkout_empty_cart(test_client):
    _, headers = register_and_login(test_client)

    response = test_client.post(
        "/orders/checkout",
        headers=headers,
    )

    assert response.status_code == 400


def test_checkout_inactive_product(test_client):
    username, headers = register_and_login(test_client)

    product_id = create_product(active=False)

    add_product_to_cart(username, product_id)

    response = test_client.post(
        "/orders/checkout",
        headers=headers,
    )

    assert response.status_code == 400


def test_checkout_insufficient_stock(test_client):
    username, headers = register_and_login(test_client)

    product_id = create_product(stock=1)

    add_product_to_cart(
        username,
        product_id,
        quantity=5,
    )

    response = test_client.post(
        "/orders/checkout",
        headers=headers,
    )

    assert response.status_code == 400


def test_get_my_orders(test_client):
    username, headers = register_and_login(test_client)

    product_id = create_product()

    add_product_to_cart(username, product_id)

    test_client.post(
        "/orders/checkout",
        headers=headers,
    )

    response = test_client.get(
        "/orders",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_single_order(test_client):
    username, headers = register_and_login(test_client)

    product_id = create_product()

    add_product_to_cart(username, product_id)

    checkout = test_client.post(
        "/orders/checkout",
        headers=headers,
    )

    order_id = checkout.json()["id"]

    response = test_client.get(
        f"/orders/{order_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_cancel_pending_order(test_client):
    username, headers = register_and_login(test_client)

    product_id = create_product()

    add_product_to_cart(username, product_id)

    checkout = test_client.post(
        "/orders/checkout",
        headers=headers,
    )

    order_id = checkout.json()["id"]

    response = test_client.patch(
        f"/orders/{order_id}/cancel",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_admin_get_all_orders(test_client, admin_headers):
    response = test_client.get(
        "/orders/admin/all",
        headers=admin_headers,
    )

    assert response.status_code == 200


def test_normal_user_cannot_access_admin_orders(test_client):
    _, headers = register_and_login(test_client)

    response = test_client.get(
        "/orders/admin/all",
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_update_status(test_client, admin_headers):
    username, headers = register_and_login(test_client)

    product_id = create_product()

    add_product_to_cart(username, product_id)

    checkout = test_client.post(
        "/orders/checkout",
        headers=headers,
    )

    order_id = checkout.json()["id"]

    response = test_client.patch(
        f"/orders/{order_id}/status",
        json={
            "status": "CONFIRMED",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"