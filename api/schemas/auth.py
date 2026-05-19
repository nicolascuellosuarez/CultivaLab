from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=30)
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=30)
    password: str = Field(..., min_length=8)


class RegisterAdminRequest(BaseModel):
    admin_key: str = Field(..., description="Master Key for Admin Sign - In")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
