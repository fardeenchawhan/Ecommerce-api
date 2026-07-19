from pydantic import BaseModel, EmailStr, Field


class UserResponseSchema(BaseModel):
    id: int

    name: str = Field(
        ...,
        description="Full name of the user",
        examples=["John Doe"],
    )

    username: str = Field(
        ...,
        description="Unique username",
        examples=["johndoe"],
    )

    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["john@example.com"],
    )

    is_admin: bool = Field(
        ...,
        description="Whether the user has administrator privileges",
    )

    model_config = {
        "from_attributes": True
    }


class PublicUserResponseSchema(BaseModel):
    id: int

    name: str = Field(
        ...,
        description="Full name",
        examples=["John Doe"],
    )

    username: str = Field(
        ...,
        description="Username",
        examples=["johndoe"],
    )

    model_config = {
        "from_attributes": True
    }


class UpdateProfileSchema(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        examples=["John Doe"],
        description="Updated full name",
    )

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        examples=["john_doe"],
        description="Updated username",
    )

    email: EmailStr | None = Field(
        default=None,
        examples=["john@example.com"],
        description="Updated email address",
    )


class ChangePasswordSchema(BaseModel):
    current_password: str

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="New password",
    )


class MessageResponseSchema(BaseModel):
    message: str = Field(
        ...,
        examples=["Profile updated successfully."],
    )