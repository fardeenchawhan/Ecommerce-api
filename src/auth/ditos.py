from pydantic import BaseModel, EmailStr


class RegisterSchema(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    username: str
    password: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"