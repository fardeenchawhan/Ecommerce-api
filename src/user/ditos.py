from pydantic import BaseModel, EmailStr


class UserResponseSchema(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    is_admin: bool

    model_config = {
        "from_attributes": True
    }