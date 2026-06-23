from fastapi import APIRouter, Depends, status

from src.user.ditos import UserResponseSchema
from src.user.models import Usermodel
from src.utils.helpers import get_current_user


user_routes = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@user_routes.get(
    "/me",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get current logged-in user"
)
async def get_me(user: Usermodel = Depends(get_current_user)):
    return user