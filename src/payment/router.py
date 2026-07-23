from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.payment import controller
from src.payment.ditos import (
    PaymentCreateResponseSchema,
    PaymentVerifySchema,
)
from src.utils.db import get_db
from src.utils.helpers import get_current_user
from src.user.models import Usermodel

payment_router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@payment_router.post(
    "/create/{order_id}",
    response_model=PaymentCreateResponseSchema,
    summary="Create Razorpay Order",
description="Creates a Razorpay payment order for an authenticated user's order."
)
async def create_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.create_payment(
        order_id,
        db,
        current_user,
    )


@payment_router.post(
        "/verify",
        summary="Verify Payment",
        description="Verifies a successful Razorpay payment and confirms the order."
        )
async def verify_payment(
    body: PaymentVerifySchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.verify_payment(
        body,
        db,
        current_user,
    )


@payment_router.post(
        "/refund/{order_id}",
        summary="Refund Order",
description="Refunds a paid order and restores product inventory. Admin only."
)
async def refund_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.refund_payment(
        order_id,
        db,
        current_user,
    )


@payment_router.post(
        "/webhook",
        summary="Razorpay Webhook",
description="Receives payment events sent by Razorpay."
)
async def razorpay_webhook(request: Request):

    body = await request.body()

    signature = request.headers.get(
        "X-Razorpay-Signature"
    )

    return {
        "received": True
    }