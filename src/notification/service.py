from fastapi import BackgroundTasks

from src.email.service import send_email
from src.email.templates import welcome_email_template
from src.email.templates import (
    order_status_template,
)
from src.email.templates import (
    welcome_email_template,
    order_confirmation_template,
)

def send_welcome_email(
    background_tasks: BackgroundTasks,
    email: str,
    name: str,
):
    background_tasks.add_task(
        send_email,
        to_email=email,
        subject="Welcome to Ecommerce API",
        html=welcome_email_template(name),
    )


def send_order_status_email(
    background_tasks,
    email: str,
    name: str,
    order_id: int,
    status: str,
):
    background_tasks.add_task(
        send_email,
        to_email=email,
        subject="Order Status Updated",
        html=order_status_template(
            name,
            order_id,
            status,
        ),
    )


def send_order_confirmation_email(
    background_tasks,
    email: str,
    name: str,
    order_id: int,
    total,
):
    background_tasks.add_task(
        send_email,
        to_email=email,
        subject="Your Order is Confirmed",
        html=order_confirmation_template(
            name,
            order_id,
            total,
        ),
    )