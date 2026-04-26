from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID
from pydantic import EmailStr


# ─── Pydantic models for users ─────────────────────────────────────────────────

# Base for API schemas (no id, no hashed_password, no table=True)
class UserBase(SQLModel):
    email: EmailStr = Field(max_length=255)

# request: a password is in plaintext
class UserSignupLogin(UserBase):
    password: str

# SignUp Responce
class UserSignupResponse(UserBase):
    id: UUID

# This model defines the user object inside the token response
class UserLoginResponse(UserBase):
    id: UUID
    tenant_id: UUID
    role: str
    is_active: bool

# This is the main response model for the /login endpoint
class AuthTokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int # Or timedelta, Pydantic will handle it
    user: UserLoginResponse


# ─── Pydantic models for tenants ─────────────────────────────────────────────────

class TenantsBase(SQLModel):
    name: str

# class TenantsSignupLogin(TenantsBase):
#     pass

class TenantsResponse(TenantsBase):
    id: UUID
    created_at: datetime
