from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import (
    Column, ForeignKeyConstraint, PrimaryKeyConstraint,
    text, Text, DateTime, Index, Numeric,
)
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from datetime import datetime
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.users import Tenants


# ─── ORM SQLMOdel model for agents ─────────────────────────────────────────────────

class Agents(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='agents_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='agents_pkey')
    )
    # Primary key, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    created_at: datetime = Field(sa_column=Column(
            'created_at', 
            DateTime(True), 
            nullable=False, 
            server_default=text('now()')
        )
    )
    # Core fields
    agent_type: str = Field(max_length=50, nullable=False)
    name: str = Field(max_length=255, nullable=False)
    
    capabilities: dict = Field(sa_column=Column(
            'capabilities', 
            JSONB, 
            nullable=False, 
            server_default=text("'[]'::jsonb")
        )
    )
    is_active: bool = Field(nullable=False, sa_column_kwargs={"server_default": text("true")})
    # Foreign keys
    tenant_id: UUID = Field(nullable=False)
    # Relationship attributes
    tenant: 'Tenants' = Relationship(back_populates='agents')
    agent_interactions: list['AgentInteractions'] = Relationship(back_populates='agent')


# ─── ORM SQLMOdel model for agent_interections ─────────────────────────────────────────────────

class AgentInteractions(SQLModel, table=True):
    __tablename__ = 'agent_interactions'
    __table_args__ = (
        ForeignKeyConstraint(['agent_id'], ['agents.id'], name='agent_interactions_agent_id_fkey'),
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='agent_interactions_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='agent_interactions_pkey'),
        Index('idx_agent_interactions_agent', 'agent_id', text('created_at DESC')),
        Index('idx_agent_interactions_tenant', 'tenant_id', text('created_at DESC'))
    )
    # Primary key, Core fields, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    created_at: datetime = Field(sa_column=Column(
            'created_at', 
            DateTime(True), 
            nullable=False, 
            server_default=text('now()')
        )
    )
    
    # Core fields
    source: str = Field(max_length=50, nullable=False)
    raw_input: str = Field(sa_column=Column('raw_input', Text, nullable=False))
    parsed_intent: str | None = Field(default=None, max_length=255) 
    confidence_score: Decimal | None = Field(default=None, sa_column=Column('confidence_score', Numeric(3, 2)))
    tool_calls: dict | None = Field(
        default=None, 
        sa_column=Column(
            'tool_calls', 
            JSONB, 
            server_default=text("'[]'::jsonb")
        )
    )
    response_text: str | None = Field(default=None, sa_column=Column('response_text', Text))
    latency_ms: int | None = Field(default=None)
    error: str | None = Field(default=None, sa_column=Column('error', Text))

    # Foreign keys
    tenant_id: UUID = Field(nullable=False)
    agent_id: UUID = Field(nullable=False)
    # Relationship attributes
    agent: 'Agents' = Relationship(back_populates='agent_interactions')
    tenant: 'Tenants' = Relationship(back_populates='agent_interactions')
