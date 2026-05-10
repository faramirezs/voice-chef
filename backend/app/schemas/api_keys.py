from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


# ─── Pydantic models for API Keys ─────────────────────────────────────────

class APIKeyBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_active: bool = Field(default=True)


class APIKeyCreate(APIKeyBase):
    """Request model for creating a new API key"""
    pass


class APIKeyUpdate(SQLModel):
    """Request model for updating an API key"""
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_active: Optional[bool] = Field(default=None)


class APIKeyResponse(APIKeyBase):
    """Response model for API key endpoints (doesn't include the full key)"""
    id: UUID
    key_preview: str
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    tenant_id: UUID


class APIKeyCreateResponse(SQLModel):
    """Response model when creating a new API key (includes the full key, shown only once)"""
    id: UUID
    name: str
    key: str  # Full API key, only shown at creation time
    key_preview: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    tenant_id: UUID


class APIKeyListResponse(SQLModel):
    """Response model for listing API keys"""
    id: UUID
    name: str
    key_preview: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
    tenant_id: UUID
