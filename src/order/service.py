from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.order.enums import OrderStatus
from src.order.models import OrderModel
from src.product.models import ProductModel


def cancel_order(
    order: OrderModel,
    db: Session,
):
    """
    Cancel an order and restore product stock.
    """

    # Already cancelled
    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is already cancelled."
        )

    # Cannot cancel after shipping
    if order.status in (
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order can no longer be cancelled."
        )

    # Restore stock
    for item in order.order_items:
        product = db.get(ProductModel, item.product_id)

        if product:
            product.stock += item.quantity

    order.status = OrderStatus.CANCELLED

    db.commit()
    db.refresh(order)

    return order