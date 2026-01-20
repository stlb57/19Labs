from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class OwnerSignupRequest(BaseModel):
    # Lab Details
    lab_name: str
    owner_name: str
    # Admin User Details
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: str
    address: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str        # user_id
    lab_id: str
    role_id: Optional[str] = None
    exp: int

class SetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
