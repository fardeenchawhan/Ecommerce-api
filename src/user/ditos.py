from pydantic import BaseModel, EmailStr, Field


class UserResponseSchema(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    is_admin: bool

    model_config = {
        "from_attributes": True
    }


class PublicUserResponseSchema(BaseModel):
    id: int
    name: str
    username: str

    model_config = {
        "from_attributes": True
    }


class UpdateProfileSchema(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None


class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str


class MessageResponseSchema(BaseModel):
    message: str