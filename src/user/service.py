from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.controller import (
    get_password_hash,
    verify_password,
)
from src.user.ditos import (
    UpdateProfileSchema,
    ChangePasswordSchema,
)
from src.user.models import Usermodel


def get_me(
    current_user: Usermodel,
):
    return current_user


def update_profile(
    body: UpdateProfileSchema,
    db: Session,
    current_user: Usermodel,
):
    update_data = body.model_dump(exclude_unset=True)

    if "username" in update_data:
        existing_user = (
            db.execute(
                select(Usermodel).where(
                    Usermodel.username == update_data["username"],
                    Usermodel.id != current_user.id,
                )
            )
            .scalar_one_or_none()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists.",
            )

    if "email" in update_data:
        existing_user = (
            db.execute(
                select(Usermodel).where(
                    Usermodel.email == update_data["email"],
                    Usermodel.id != current_user.id,
                )
            )
            .scalar_one_or_none()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists.",
            )

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


def change_password(
    body: ChangePasswordSchema,
    db: Session,
    current_user: Usermodel,
):
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password.",
        )
    
    if not verify_password(
        body.current_password,
        current_user.hash_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    if verify_password(
        body.new_password,
        current_user.hash_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password.",
        )

    current_user.hash_password = get_password_hash(
        body.new_password
    )

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Password changed successfully."
    }