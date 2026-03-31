from datetime import datetime
from typing import List, TYPE_CHECKING, Optional
import uuid
from uuid import UUID

from sqlalchemy import text, DateTime, Column, UniqueConstraint
from sqlalchemy import Boolean, Index
from sqlmodel import SQLModel, Field, Relationship

# NOTE: MP. We provide Pylance with a hint, but in a way that avoids triggering 
# a circular import during execution.
if TYPE_CHECKING:
    from .recipe_models import Recipe


class Users(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint('email', name='users_email_key'),
        Index("ix_users_email", "email", unique=True),
    )
    id: uuid.UUID = Field(
        default=None, 
        primary_key=True, 
        sa_column_kwargs={"server_default": text("gen_random_uuid()")} # db-side UUID generation
    )
    email: str = Field(max_length=255, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(
        default=None, # Python should not generate a value
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=text("now()")
        ),
    )
    updated_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
            onupdate=text("now()"),
        ),
    )
    role: str = Field(
        default="editor", # default is for Python
        max_length=50,
        nullable=False,
        sa_column_kwargs={"server_default": text("'editor'")} # server_default is for the database (ALTER TABLE ... DEFAULT ...)
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("true")}
    )

    # Foreign keys
    tenant_id: UUID | None = Field(default=None, foreign_key="tenants.id") 

    # Relationship attributes. "Tenants" | None is a forward references
    tenant: Optional["Tenants"] = Relationship(back_populates='users')
    recipes: List["Recipe"] = Relationship(back_populates="created_by_user")


class Tenants(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint('slug', name='tenants_slug_key'),
        Index("ix_tenants_slug", "slug", unique=True),
    )
    id: UUID = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")}
    )
    created_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=text("now()")
        ),
    )
    updated_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
            onupdate=text("now()"),
        ),
    )
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=100)
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text('true'))
    )
    settings: str | None = Field(default=None) # column is of type character varying

    # Relationship attributes
    users: List['Users'] = Relationship(back_populates='tenant')
    recipes: List['Recipe'] = Relationship(back_populates="tenant")
    # the line below can be uncomment when there is Igredient table
    # ingredients: List['Ingredient'] = Relationship(back_populates="tenant")
