from pydantic import BaseModel


class PaymentCreateResponseSchema(BaseModel):
    razorpay_order_id: str
    amount: int
    currency: str
    key_id: str



class PaymentVerifySchema(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str