from fastapi import FastAPI
import os
# import models so tables are registered
from src.dashboard.router import dashboard_routes
# routers
from src.auth.router import auth_routes
from src.user.router import user_routes
from src.category.router import category_routes
from src.product.router import product_routes
from src.cart.router import cart_routes
from src.order.router import order_routes
from src.ai.router import ai_router
from contextlib import asynccontextmanager
from src.user.controller import create_admin_if_not_exists
from src.review.router import review_routes
from src.exceptions.handlers import register_exception_handlers
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.redis import redis_client
from src.utils.logger import LoggingMiddleware
from src.payment.router import payment_router


tags_metadata = [
    {
        "name": "Authentication",
        "description": "User registration and authentication.",
    },
    {
        "name": "Users",
        "description": "User profile management.",
    },
    {
        "name": "Categories",
        "description": "Product categories.",
    },
    {
        "name": "Products",
        "description": "Browse and manage products.",
    },
    {
        "name": "Cart",
        "description": "Shopping cart operations.",
    },
    {
        "name": "Orders",
        "description": "Order management.",
    },
    {
        "name": "Payments",
        "description": "Razorpay payment integration.",
    },
    {
        "name": "Reviews",
        "description": "Product reviews and ratings.",
    },
    {
        "name": "AI",
        "description": "AI-powered search and metadata generation.",
    },
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client.ping()

    if os.getenv("TESTING") != "1":
        create_admin_if_not_exists()

    yield


app = FastAPI(
    title="E-Commerce API",
    description="Production-ready FastAPI backend for an E-commerce platform.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    BaseHTTPMiddleware,
    dispatch=LoggingMiddleware(),
)

register_exception_handlers(app)

app.include_router(auth_routes)
app.include_router(dashboard_routes)
app.include_router(user_routes)
app.include_router(category_routes)
app.include_router(product_routes)
app.include_router(cart_routes)
app.include_router(order_routes)
app.include_router(review_routes)
app.include_router(ai_router)
app.include_router(payment_router)

@app.get(
        "/",
        tags=["System"],
        summary="API Information",
        description="Returns basic information about the E-commerce API."
        )
async def root():
    return {
        "message": "E-Commerce API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
        "/health",
        tags=["System"], 
        summary="Health Check",
        description="Returns the application's health status."
)
async def health():
    return {"status": "healthy"}

from src.utils.redis import redis_client


@app.get(
        "/redis-test",
        summary="Redis Test",
        description="Tests the Redis connection."
        )
async def redis_test():

    redis_client.set("hello", "world")

    value = redis_client.get("hello")

    return {
        "redis": value
    }