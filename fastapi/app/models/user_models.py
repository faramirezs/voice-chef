<<<<<<< HEAD
from typing import Optional, TYPE_CHECKING
import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKeyConstraint, PrimaryKeyConstraint, String, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel
=======
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text, Column, UniqueConstraint
from sqlalchemy import Boolean, Index
import uuid
from uuid import UUID
from typing import List, TYPE_CHECKING, Optional
from sqlalchemy import DateTime # database column type: `timestamp with time zone`
from datetime import datetime   # Python type: type hints and runtime values

>>>>>>> 113bd3b (fix. UUID generation + doc update on this matter)

if TYPE_CHECKING:
<<<<<<< HEAD
    from app.models.recipe_models import Recipes
=======
    from .recipe_models import Recipe


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
>>>>>>> 113bd3b (fix. UUID generation + doc update on this matter)


class Tenants(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tenants_pkey'),
        UniqueConstraint('slug', name='tenants_slug_key')
    )
<<<<<<< HEAD
=======
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
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=100)
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text('true'))
    )
    settings: str | None = Field(default=None) # column is of type character varying
>>>>>>> 113bd3b (fix. UUID generation + doc update on this matter)

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    slug: str = Field(sa_column=Column('slug', String(100), nullable=False))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    settings: Optional[dict] = Field(default=None, sa_column=Column('settings', JSONB, server_default=text("'{}'")))

    agents: list['Agents'] = Relationship(back_populates='tenant')
    categories: list['Categories'] = Relationship(back_populates='tenant')
    ingredients: list['Ingredients'] = Relationship(back_populates='tenant')
    shopping_lists: list['ShoppingLists'] = Relationship(back_populates='tenant')
    tags: list['Tags'] = Relationship(back_populates='tenant')
    task_lists: list['TaskLists'] = Relationship(back_populates='tenant')
    users: list['Users'] = Relationship(back_populates='tenant')
    agent_interactions: list['AgentInteractions'] = Relationship(back_populates='tenant')
    recipes: list['Recipes'] = Relationship(back_populates='tenant')


class Users(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='users_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    tenant_id: uuid.UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))
    email: str = Field(sa_column=Column('email', String(320), nullable=False))
    password_hash: str = Field(sa_column=Column('password_hash', String(255), nullable=False))
    role: str = Field(sa_column=Column('role', String(50), nullable=False, server_default=text("'editor'::character varying")))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

    tenant: 'Tenants' = Relationship(back_populates='users')
    recipes: list['Recipes'] = Relationship(back_populates='users')
