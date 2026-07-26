from uuid import uuid4

from sqlalchemy import select

from src.order.enums import OrderStatus
from src.order.models import OrderItemModel, OrderModel
from src.product.models import ProductModel
from src.review.models import ReviewModel
from src.user.models import Usermodel
from src.utils.db import SessionLocal


# ==========================================================
# Helpers
# ==========================================================

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


def create_product():
    db = SessionLocal()

    product = ProductModel(
        name=f"Phone {uuid4().hex[:6]}",
        description="Test Product",
        price=1000,
        stock=10,
        brand="Apple",
        sku=f"SKU-{uuid4().hex[:8]}",
        category_id=1,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    product_id = product.id

    db.close()

    return product_id


def create_delivered_order(username, product_id):
    db = SessionLocal()

    user = db.execute(
        select(Usermodel).where(
            Usermodel.username == username
        )
    ).scalar_one()

    order = OrderModel(
        user_id=user.id,
        total_amount=1000,
        total_items=1,
        status=OrderStatus.DELIVERED,
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    item = OrderItemModel(
        order_id=order.id,
        product_id=product_id,
        quantity=1,
        unit_price=1000,
    )

    db.add(item)
    db.commit()

    db.close()


def create_review(db, user_id, product_id):
    review = ReviewModel(
        rating=5,
        comment="Excellent",
        user_id=user_id,
        product_id=product_id,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review.id


# ==========================================================
# Tests
# ==========================================================

def test_create_review_success(test_client):

    username = register_user(test_client)

    headers = login_user(
        test_client,
        username,
    )

    product_id = create_product()

    create_delivered_order(
        username,
        product_id,
    )

    response = test_client.post(
        f"/reviews/product/{product_id}",
        json={
            "rating": 5,
            "comment": "Excellent product",
        },
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["rating"] == 5
    assert data["comment"] == "Excellent product"


def test_duplicate_review(test_client):

    username = register_user(test_client)

    headers = login_user(
        test_client,
        username,
    )

    product_id = create_product()

    create_delivered_order(
        username,
        product_id,
    )

    payload = {
        "rating": 5,
        "comment": "Nice",
    }

    test_client.post(
        f"/reviews/product/{product_id}",
        json=payload,
        headers=headers,
    )

    response = test_client.post(
        f"/reviews/product/{product_id}",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["message"] == "You have already reviewed this product."


def test_review_without_purchase(test_client):

    username = register_user(test_client)

    headers = login_user(
        test_client,
        username,
    )

    product_id = create_product()

    response = test_client.post(
        f"/reviews/product/{product_id}",
        json={
            "rating": 5,
            "comment": "Nice",
        },
        headers=headers,
    )

    assert response.status_code == 403


def test_update_review(test_client):

    username = register_user(test_client)

    headers = login_user(
        test_client,
        username,
    )

    product_id = create_product()

    create_delivered_order(
        username,
        product_id,
    )

    response = test_client.post(
        f"/reviews/product/{product_id}",
        json={
            "rating": 5,
            "comment": "Good",
        },
        headers=headers,
    )

    review_id = response.json()["id"]

    response = test_client.patch(
        f"/reviews/{review_id}",
        json={
            "rating": 4,
            "comment": "Updated",
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["rating"] == 4
    assert data["comment"] == "Updated"


def test_delete_review(test_client):

    username = register_user(test_client)

    headers = login_user(
        test_client,
        username,
    )

    product_id = create_product()

    create_delivered_order(
        username,
        product_id,
    )

    response = test_client.post(
        f"/reviews/product/{product_id}",
        json={
            "rating": 5,
            "comment": "Nice",
        },
        headers=headers,
    )

    review_id = response.json()["id"]

    response = test_client.delete(
        f"/reviews/{review_id}",
        headers=headers,
    )

    assert response.status_code == 200


def test_get_my_reviews(test_client):

    username = register_user(test_client)

    headers = login_user(
        test_client,
        username,
    )

    product_id = create_product()

    create_delivered_order(
        username,
        product_id,
    )

    test_client.post(
        f"/reviews/product/{product_id}",
        json={
            "rating": 5,
            "comment": "Nice",
        },
        headers=headers,
    )

    response = test_client.get(
        "/reviews/me",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_product_reviews(test_client):

    product_id = create_product()

    response = test_client.get(
        f"/reviews/product/{product_id}"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_product_rating(test_client):

    product_id = create_product()

    response = test_client.get(
        f"/reviews/product/rating/{product_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert "average_rating" in data
    assert "total_reviews" in data


def test_normal_user_cannot_access_admin_reviews(test_client):

    username = register_user(test_client)

    headers = login_user(
        test_client,
        username,
    )

    response = test_client.get(
        "/reviews/admin/all",
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_get_all_reviews(test_client):

    headers = login_admin(test_client)

    response = test_client.get(
        "/reviews/admin/all",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)