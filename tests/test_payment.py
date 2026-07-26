from unittest.mock import patch
from uuid import uuid4

from src.order.enums import PaymentStatus

from decimal import Decimal
from unittest.mock import patch

from sqlalchemy import select

from src.category.models import CategoryModel
from src.product.models import ProductModel
from src.order.models import OrderModel
from src.order.enums import PaymentStatus
from src.utils.db import SessionLocal
import jwt
from src.utils.settings import settings

def create_product():
    db = SessionLocal()

    category = db.execute(
        select(CategoryModel).where(
            CategoryModel.name == "Electronics"
        )
    ).scalar_one()

    product = ProductModel(
        name="iPhone",
        description="Test Product",
        brand="Apple",
        price=Decimal("1000.00"),
        stock=10,
        sku=f"SKU-{uuid4().hex[:8]}",
        category_id=category.id,
        is_active=True,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    db.close()

    return product


def create_order(test_client, user_headers):
    product = create_product()

    test_client.post(
        "/cart",
        json={
            "product_id": product.id,
            "quantity": 2,
        },
        headers=user_headers,
    )

    response = test_client.post(
        "/orders/checkout",
        headers=user_headers,
    )

    assert response.status_code == 201

    return response


@patch("src.payment.controller.create_payment_order")
def test_create_payment_success(
    mock_payment,
    test_client,
    user_headers,
):
    order = create_order(test_client, user_headers).json()

    mock_payment.return_value = {
        "id": "order_test123",
        "amount": 200000,
        "currency": "INR",
    }

    response = test_client.post(
        f"/payments/create/{order['id']}",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["razorpay_order_id"] == "order_test123"


def test_create_payment_order_not_found(
    test_client,
    user_headers,
):
    response = test_client.post(
        "/payments/create/999999",
        headers=user_headers,
    )

    assert response.status_code == 404


@patch("src.payment.controller.verify_payment_signature")
def test_verify_payment_success(
    mock_verify,
    test_client,
    user_headers,
):
    order = create_order(test_client, user_headers).json()

    db = SessionLocal()

    db_order = db.get(OrderModel, order["id"])

    token = user_headers["Authorization"].split()[1]

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    razorpay_order_id = f"order_{uuid4().hex}"

    db_order.razorpay_order_id = razorpay_order_id

    db.commit()

    db.close()

    payload = {
    "razorpay_order_id": razorpay_order_id,
    "razorpay_payment_id": f"pay_{uuid4().hex}",
    "razorpay_signature": "signature",
}

    response = test_client.post(
        "/payments/verify",
        json=payload,
        headers=user_headers,
    )

    assert response.status_code == 200


@patch("src.payment.controller.verify_payment_signature")
def test_verify_payment_twice(
    mock_verify,
    test_client,
    user_headers,
):
    order = create_order(test_client, user_headers).json()

    db = SessionLocal()

    db_order = db.get(OrderModel, order["id"])

    razorpay_order_id = f"order_{uuid4().hex}"
    
    db_order.razorpay_order_id = razorpay_order_id

    db_order.payment_status = PaymentStatus.PAID

    db.commit()

    db.close()

    payload = {
    "razorpay_order_id": razorpay_order_id,
    "razorpay_payment_id": f"pay_{uuid4().hex}",
    "razorpay_signature": "signature",
}

    response = test_client.post(
        "/payments/verify",
        json=payload,
        headers=user_headers,
    )

    assert response.status_code == 400


@patch("src.payment.controller.verify_payment_signature")
def test_refund_paid_order(
    mock_verify,
    test_client,
    user_headers,
):
    order = create_order(test_client, user_headers).json()

    db = SessionLocal()

    db_order = db.get(OrderModel, order["id"])

    razorpay_order_id = f"order_{uuid4().hex}"
      
    db_order.razorpay_order_id = razorpay_order_id
    db.commit()

    db.close()

    payload = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": f"pay_{uuid4().hex}",
        "razorpay_signature": "signature",
    }

    test_client.post(
        "/payments/verify",
        json=payload,
        headers=user_headers,
    )

    response = test_client.post(
        f"/payments/refund/{order['id']}",
        headers=user_headers,
    )

    assert response.status_code == 200


def test_refund_unpaid_order(
    test_client,
    user_headers,
):
    order = create_order(test_client, user_headers).json()

    response = test_client.post(
        f"/payments/refund/{order['id']}",
        headers=user_headers,
    )

    assert response.status_code == 400