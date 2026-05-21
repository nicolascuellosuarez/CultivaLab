from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: str
    username: str
    role: str


class UserUpdateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class PasswordUpdateRequest(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
