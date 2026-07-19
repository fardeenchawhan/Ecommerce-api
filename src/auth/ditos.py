from pydantic import BaseModel, EmailStr, Field


class RegisterSchema(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["John Doe"],
        description="Full name of the user",
    )

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        examples=["johndoe"],
        description="Unique username",
    )

    email: EmailStr = Field(
        ...,
        examples=["john@example.com"],
        description="User email address",
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        examples=["StrongPassword123"],
        description="User password",
    )


class LoginSchema(BaseModel):
    username: str = Field(
        ...,
        examples=["johndoe"],
        description="Registered username",
    )

    password: str = Field(
        ...,
        examples=["StrongPassword123"],
        description="User password",
    )


class TokenResponseSchema(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT Access Token",
    )

    token_type: str = Field(
        default="bearer",
        description="Authentication scheme",
    )