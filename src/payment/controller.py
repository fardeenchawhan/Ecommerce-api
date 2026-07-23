from decimal import Decimal

from sqlalchemy.orm import Session

from src.order.models import OrderModel
from src.product.models import ProductModel
from src.payment.service import create_payment_order
from src.utils.settings import settings
from fastapi import HTTPException, status
from src.payment.ditos import PaymentVerifySchema
from src.order.enums import OrderStatus
from src.order.models import PaymentStatus
from src.payment.service import verify_payment_signature
from src.cache.service import delete_pattern
from sqlalchemy import update
from src.user.models import Usermodel

def create_payment(
    order_id: int,
    db: Session,
    current_user: Usermodel,
):
    order = db.get(OrderModel, order_id)

    # -----------------------------
    # Order exists
    # -----------------------------
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    # -----------------------------
    # Order belongs to current user
    # -----------------------------
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to pay for this order.",
        )

    # -----------------------------
    # Cannot pay cancelled order
    # -----------------------------
    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled orders cannot be paid.",
        )

    # -----------------------------
    # Already paid
    # -----------------------------
    if order.payment_status == PaymentStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has already been paid.",
        )

    amount = int(Decimal(order.total_amount) * 100)

    # -----------------------------
    # Reuse existing Razorpay order
    # -----------------------------
    if order.razorpay_order_id:
        return {
            "razorpay_order_id": order.razorpay_order_id,
            "amount": amount,
            "currency": "INR",
            "key_id": settings.RAZORPAY_KEY_ID,
        }

    # -----------------------------
    # Create new Razorpay order
    # -----------------------------
    payment = create_payment_order(amount)

    order.razorpay_order_id = payment["id"]

    db.commit()
    db.refresh(order)

    return {
        "razorpay_order_id": payment["id"],
        "amount": payment["amount"],
        "currency": payment["currency"],
        "key_id": settings.RAZORPAY_KEY_ID,
    }



def verify_payment(
    body: PaymentVerifySchema,
    db: Session,
    current_user: Usermodel,
):
    verify_payment_signature(
        razorpay_order_id=body.razorpay_order_id,
        razorpay_payment_id=body.razorpay_payment_id,
        razorpay_signature=body.razorpay_signature,
    )

    order = (
        db.query(OrderModel)
        .filter(
            OrderModel.razorpay_order_id == body.razorpay_order_id
        )
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found.",
        )

    if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized."
            )

    if order.payment_status == PaymentStatus.PAID:
        raise HTTPException(
            status_code=400,
            detail="Payment already verified."
        )

    if order.razorpay_order_id != body.razorpay_order_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid order."
        )


    for item in order.order_items:

        result = db.execute(
            update(ProductModel)
            .where(
                ProductModel.id == item.product_id,
                ProductModel.stock >= item.quantity,
            )
            .values(
                stock=ProductModel.stock - item.quantity
            )
        )

        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"{item.product.name} is out of stock."
            )

    order.payment_status = PaymentStatus.PAID
    order.status = OrderStatus.CONFIRMED
    order.razorpay_payment_id = body.razorpay_payment_id

    db.commit()
    db.refresh(order)

    delete_pattern("products:*")

    return {
        "message": "Payment verified successfully."
    }



def refund_payment(
    order_id: int,
    db: Session,
    current_user: Usermodel,
):
    order = db.get(OrderModel, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )

    # Only the owner of the order can request a refund
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to refund this order."
        )

    if order.payment_status != PaymentStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only paid orders can be refunded."
        )

    # Do not allow refund after shipping
    if order.status in (
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund is not allowed after shipping."
        )

    # Restore stock
    for item in order.order_items:

        db.execute(
            update(ProductModel)
            .where(
                ProductModel.id == item.product_id
            )
            .values(
                stock=ProductModel.stock + item.quantity
            )
        )

    order.payment_status = PaymentStatus.REFUNDED
    order.status = OrderStatus.CANCELLED

    db.commit()
    db.refresh(order)

    delete_pattern("products:*")

    return {
        "message": "Refund processed successfully."
    }