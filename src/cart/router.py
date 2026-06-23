from fastapi import APIRouter

cart_routes = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)