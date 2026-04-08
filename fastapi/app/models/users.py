from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text, Column, UniqueConstraint
from sqlalchemy import Boolean, Index
import uuid
from uuid import UUID
from typing import List, TYPE_CHECKING, Optional
from sqlalchemy import DateTime # database column type: `timestamp with time zone`
from datetime import datetime   # Python type: type hints and runtime values


# NOTE: MP. We provide Pylance with a hint, but in a way that avoids triggering 
# a circular import during execution.
if TYPE_CHECKING:
    from .tmp_recipe import Recipe


class Users(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint('email', name='users_email_key'),
        Index("ix_users_email", "email", unique=True),
    )
    id: uuid.UUID = Field(
        # app-side UUID generation for MVP delivery
        default_factory=uuid.uuid4,
        # scheduling DB-enforced UUID defaults as post-MVP hardening
        # sa_column_kwargs={"server_default": text("gen_random_uuid()")}
        primary_key=True,
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
        sa_column_kwargs={"server_default": text("'editor'::character varying")} # server_default is for the database (ALTER TABLE ... DEFAULT ...)
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
        Index("ix_tenants_name", "name")
    )
    id: UUID = Field(
        # app-side UUID generation for MVP delivery
        default_factory=uuid.uuid4,
        # scheduling DB-enforced UUID defaults as post-MVP hardening
        # sa_column_kwargs={"server_default": text("gen_random_uuid()")}
        primary_key=True,
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
    name: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=100, nullable=False)
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text('true'))
    )
    settings: str | None = None # column is of type character varying

    # Relationship attributes
    users: List['Users'] = Relationship(back_populates='tenant')
    recipes: List['Recipe'] = Relationship(back_populates="tenant")
    # the line below can be uncomment when there is Igredient table
    # ingredients: List['Ingredient'] = Relationship(back_populates="tenant")
