from pydantic import BaseModel, EmailStr,Field
from typing import Optional

class RegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


class LoginResponse(BaseModel):
    message: str
    token: str
    user: UserResponse

class UserDetailResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: str


class LogoutResponse(BaseModel):
    message: str