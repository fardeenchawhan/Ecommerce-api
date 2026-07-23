from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.user import service
from src.user.ditos import (
    UserResponseSchema,
    UpdateProfileSchema,
    ChangePasswordSchema,
    MessageResponseSchema
)
from src.user.models import Usermodel
from src.utils.db import get_db
from src.utils.helpers import get_current_user


user_routes = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@user_routes.get(
    "/me",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Returns the authenticated user's profile.",
)
async def get_me(
    current_user: Usermodel = Depends(get_current_user),
):
    return service.get_me(current_user)


@user_routes.patch(
    "/me",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update Profile",
    description="Updates the authenticated user's profile information.",
)
async def update_profile(
    body: UpdateProfileSchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return service.update_profile(
        body,
        db,
        current_user,
    )


@user_routes.patch(
    "/change-password",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Change Password",
    description="Changes the authenticated user's password.",
)
async def change_password(
    body: ChangePasswordSchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return service.change_password(
        body,
        db,
        current_user,
    )