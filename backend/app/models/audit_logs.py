from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import (
    Column,
    DateTime,
    Index,
    PrimaryKeyConstraint,
    String,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB


# ─── ORM SQLMOdel model for audit_logs ─────────────────────────────────────────────────

class AuditLogs(SQLModel, table=True):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='audit_logs_pkey'),
        Index('idx_audit_logs_entity', 'entity', 'entity_id'),
        Index('idx_audit_logs_tenant', 'tenant_id', text('created_at DESC'))
    )
    # Primary key, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    tenant_id: UUID = Field(nullable=False)
    created_at: datetime = Field(sa_column=Column(
            'created_at', DateTime(True), nullable=False, server_default=text('now()')))
    
    # Core fields
    actor_type: str = Field(
        sa_column=Column('actor_type', String(50), nullable=False))
    actor_id: UUID = Field(
        sa_column=Column('actor_id', Uuid, nullable=False))
    action: str = Field(
        sa_column=Column('action', String(50), nullable=False))
    entity: str = Field(
        sa_column=Column('entity', String(100), nullable=False))
    entity_id: UUID | None = Field(
        default=None, sa_column=Column('entity_id', Uuid))
    old_data: dict | None = Field(default=None, sa_column=Column('old_data', JSONB))
    new_data: dict | None = Field(default=None, sa_column=Column('new_data', JSONB))
