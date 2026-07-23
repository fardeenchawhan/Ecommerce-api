from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.payment import controller
from src.payment.ditos import PaymentCreateResponseSchema
from src.utils.db import get_db
from src.payment.ditos import PaymentVerifySchema

payment_router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@payment_router.post(
    "/create/{order_id}",
    response_model=PaymentCreateResponseSchema,
)
async def create_payment(
    order_id: int,
    db: Session = Depends(get_db),
):
    return controller.create_payment(
        order_id,
        db,
    )


@payment_router.post("/verify")
async def verify_payment(
    body: PaymentVerifySchema,
    db: Session = Depends(get_db),
):
    return controller.verify_payment(
        body,
        db,
    )