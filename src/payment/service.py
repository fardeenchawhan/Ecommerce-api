import razorpay

from src.utils.settings import settings

client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET,
    )
)


def create_payment_order(
    amount: int,
):
    """
    Amount must be in paise.
    Example:
    ₹999.99 -> 99999
    """

    payment = client.order.create(
        {
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1,
        }
    )

    return payment



from fastapi import HTTPException, status


def verify_payment_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
):
    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )

        return True

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature.",
        )