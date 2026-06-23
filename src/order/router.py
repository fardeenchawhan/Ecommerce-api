from fastapi import APIRouter

order_routes = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)