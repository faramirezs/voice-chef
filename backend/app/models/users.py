from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import (
    UniqueConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, 
    String, text, Column, Boolean
)
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from uuid import UUID
from typing import List, TYPE_CHECKING, Optional
from sqlalchemy import DateTime # database column type: `timestamp with time zone`


# NOTE: MP. We provide Pylance with a hint, but in a way that avoids triggering
# a circular import during execution.
if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.ingredient import Ingredient
    from app.models.categories import Categories, Tag
    from app.models.agents import Agents, AgentInteractions
    from app.models.tasks import TaskLists, ShoppingLists

# ─── ORM SQLMOdel model for users ─────────────────────────────────────────────────

class Users(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='users_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
    )
    # Primary key, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    email: str = Field(max_length=320, nullable=False)
    created_at: datetime = Field(sa_column=Column(
            'created_at', DateTime(True), 
            nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column(
            'updated_at', DateTime(True), 
            nullable=False, server_default=text('now()')))
    # Core fields
    password_hash: str = Field(max_length=255, nullable=False)
    role: str = Field(sa_column=Column(
            'role', String(50),
            nullable=False, server_default=text("'editor'")))
    is_active: bool = Field(nullable=False, sa_column_kwargs={"server_default": text("true")})
    
    # Foreign keys
    tenant_id: UUID = Field(nullable=False)

    # Relationship attributes. "Tenants" | None is a forward references
    tenant: Optional["Tenants"] = Relationship(back_populates='users')
    recipes: List["Recipe"] = Relationship(back_populates="created_by_user")


# ─── ORM SQLMOdel model for tenants ─────────────────────────────────────────────────

class Tenants(SQLModel, table=True):
    __tablename__ = "tenants"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tenants_pkey'),
        UniqueConstraint('slug', name='tenants_slug_key'),
    )
    # Primary key, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    slug: str = Field(max_length=100, nullable=False)
    created_at: datetime = Field(sa_column=Column(
            'created_at', DateTime(True), 
            nullable=False, server_default=text('now()')))
    updated_at: datetime = Field(sa_column=Column(
            'updated_at', DateTime(True), 
            nullable=False, server_default=text('now()')))
    # Core fields
    name: str = Field(max_length=255, nullable=False)
    is_active: bool = Field(nullable=False, sa_column_kwargs={"server_default": text("true")})
    settings: dict | None = Field(default=None, sa_column=Column('settings', JSONB, server_default=text("'{}'")))

    # Relationship attributes
    agents: List['Agents'] = Relationship(back_populates='tenant')
    categories: List['Categories'] = Relationship(back_populates='tenant')
    users: List['Users'] = Relationship(back_populates='tenant')
    recipes: List['Recipe'] = Relationship(back_populates="tenant")
    ingredients: List['Ingredient'] = Relationship(back_populates="tenant")
    shopping_lists: List['ShoppingLists'] = Relationship(back_populates='tenant')
    tags: List['Tag'] = Relationship(back_populates='tenant')
    task_lists: List['TaskLists'] = Relationship(back_populates='tenant')
    agent_interactions: List['AgentInteractions'] = Relationship(back_populates='tenant')
