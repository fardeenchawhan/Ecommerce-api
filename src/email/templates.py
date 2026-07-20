def welcome_email_template(name: str):
    return f"""
    <h2>Welcome {name} 👋</h2>

    <p>
        Thank you for registering with Ecommerce API.
    </p>

    <p>
        We hope you enjoy shopping with us.
    </p>
    """

def order_confirmation_template(
    name: str,
    order_id: int,
    total,
):
    return f"""
    <h2>Order Confirmed 🎉</h2>

    <p>Hi {name},</p>

    <p>Your order has been placed successfully.</p>

    <ul>
        <li><strong>Order ID:</strong> {order_id}</li>
        <li><strong>Total:</strong> ₹{total}</li>
    </ul>

    <p>Thank you for shopping with us.</p>
    """


def order_status_template(
    name: str,
    order_id: int,
    status: str,
):
    return f"""
    <h2>Order Update</h2>

    <p>Hello {name},</p>

    <p>Your order status has been updated.</p>

    <ul>
        <li>Order ID: {order_id}</li>
        <li>Status: <strong>{status}</strong></li>
    </ul>

    <p>Thank you.</p>
    """