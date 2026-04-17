from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text, Column, UniqueConstraint
from sqlalchemy import Boolean, Index, ForeignKeyConstraint, PrimaryKeyConstraint, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
import datetime
from uuid import UUID
from typing import List, TYPE_CHECKING, Optional
from sqlalchemy import DateTime # database column type: `timestamp with time zone`
from pydantic import EmailStr


# NOTE: MP. We provide Pylance with a hint, but in a way that avoids triggering
# a circular import during execution.
# In a PR comment I explained every change I did to this file and why.
if TYPE_CHECKING:
    from recipe import Recipe
    from ingredient import Ingredient
    from tmp_draft import Agents, Categories, ShoppingLists, Tags, TaskLists, AgentInteractions

# ─── ORM SQLMOdel model for users ─────────────────────────────────────────────────

class Users(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='users_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
    )
    id: UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    email: str = Field(sa_column=Column('email', String(320), nullable=False))
    # Argon2 default hash is ~97 chars. 255 provides a safe buffer.
    password_hash: str = Field(sa_column=Column('password_hash', String(255), nullable=False))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    role: str = Field(sa_column=Column('role', String(50), nullable=False, server_default=text("'editor'::character varying")))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))

    # Foreign keys
    tenant_id: UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))

    # Relationship attributes. "Tenants" | None is a forward references
    tenant: Optional["Tenants"] = Relationship(back_populates='users')
    recipes: List["Recipe"] = Relationship(back_populates="created_by_user")

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

# ─── Tenants ──────────────────────────────────────────────────────────────────

class Tenants(SQLModel, table=True):
    __tablename__ = "tenants"
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tenants_pkey'),
        UniqueConstraint('slug', name='tenants_slug_key'),
    )
    id: UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    slug: str = Field(sa_column=Column('slug', String(100), nullable=False))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    settings: Optional[dict] = Field(default=None, sa_column=Column('settings', JSONB, server_default=text("'{}'")))

    # Relationship attributes
    agents: List['Agents'] = Relationship(back_populates='tenant')
    categories: List['Categories'] = Relationship(back_populates='tenant')
    users: List['Users'] = Relationship(back_populates='tenant')
    recipes: List['Recipe'] = Relationship(back_populates="tenant")
    ingredients: List['Ingredient'] = Relationship(back_populates="tenant")
    shopping_lists: List['ShoppingLists'] = Relationship(back_populates='tenant')
    tags: List['Tags'] = Relationship(back_populates='tenant')
    task_lists: List['TaskLists'] = Relationship(back_populates='tenant')
    agent_interactions: List['AgentInteractions'] = Relationship(back_populates='tenant')

# ─── Pydantic models for tenants ─────────────────────────────────────────────────

class TenantsBase(SQLModel):
    name: str

# class TenantsSignupLogin(TenantsBase):
#     pass

class TenantsResponse(TenantsBase):
    id: UUID
    created_at: datetime.datetime
