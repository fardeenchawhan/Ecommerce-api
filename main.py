from fastapi import FastAPI
from src.utils.db import Base, engine

# import models so tables are registered
from src.dashboard.router import dashboard_routes
# routers
from src.auth.router import auth_routes
from src.user.router import user_routes
from src.category.router import category_routes
from src.product.router import product_routes
from src.cart.router import cart_routes
from src.order.router import order_routes
from contextlib import asynccontextmanager
from src.user.controller import create_admin_if_not_exists
from src.review.router import review_routes
from src.exceptions.handlers import register_exception_handlers
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.redis import redis_client
from src.utils.logger import LoggingMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client.ping()

    create_admin_if_not_exists()

    yield


app = FastAPI(
    title="E-Commerce API",
    description="""
    A FastAPI-based E-Commerce backend with:

    - JWT Authentication
    - User Management
    - Category Management
    - Product Management
    - Cart Management
    - Order Management
    """,
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


@app.get("/", tags=["System"], summary="API Information")
async def root():
    return {
        "message": "E-Commerce API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["System"], summary="Health check")
async def health():
    return {"status": "healthy"}

from src.utils.redis import redis_client


@app.get("/redis-test")
async def redis_test():

    redis_client.set("hello", "world")

    value = redis_client.get("hello")

    return {
        "redis": value
    }