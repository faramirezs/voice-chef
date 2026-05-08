from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import (
    ForeignKeyConstraint, PrimaryKeyConstraint, Column, DateTime, String,
    text, Index, UniqueConstraint
)
from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.users import Tenants

# ─── ORM SQLModel model for API Keys ─────────────────────────────────────────

class APIKeys(SQLModel, table=True):
    __tablename__ = "api_keys"
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='api_keys_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='api_keys_pkey'),
        UniqueConstraint('key_hash', name='api_keys_key_hash_key'),
        Index('idx_api_keys_tenant', 'tenant_id'),
        Index('idx_api_keys_is_active', 'is_active'),
    )

    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    name: str = Field(max_length=255, nullable=False)
    key_hash: str = Field(max_length=255, nullable=False)  # SHA-256 hash of the actual key
    key_preview: str = Field(max_length=20, nullable=False)  # First and last 4 chars of key for display
    
    description: str | None = Field(default=None, nullable=True)
    is_active: bool = Field(nullable=False, sa_column_kwargs={"server_default": text("true")})
    
    created_at: datetime = Field(sa_column=Column(
        'created_at', DateTime(True), 
        nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column(
        'updated_at', DateTime(True), 
        nullable=False, server_default=text('now()')))
    last_used_at: datetime | None = Field(default=None, sa_column=Column('last_used_at', DateTime(True)))
    
    # Foreign keys
    tenant_id: UUID = Field(nullable=False)
    
    # Relationship attributes
    tenant: Optional['Tenants'] = Relationship(back_populates='api_keys')
