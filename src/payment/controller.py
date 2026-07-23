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

def create_payment(
    order_id: int,
    db: Session,
):
    order = db.get(OrderModel, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    amount = int(
        Decimal(order.total_amount) * 100
    )

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

    order.payment_status = PaymentStatus.PAID
    order.status = OrderStatus.CONFIRMED
    order.razorpay_payment_id = body.razorpay_payment_id

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
            raise HTTPException(
                status_code=400,
                detail=f"{item.product.name} is out of stock."
            )


    db.commit()
    db.refresh(order)

    delete_pattern("products:*")

    return {
        "message": "Payment verified successfully."
    }