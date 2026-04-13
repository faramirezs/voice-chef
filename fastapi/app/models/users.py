from typing import Optional, TYPE_CHECKING
import datetime
import uuid
from pydantic import EmailStr

from sqlalchemy import Boolean, Column, DateTime, ForeignKeyConstraint, PrimaryKeyConstraint, String, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .tmp_recipe import Recipes

# ─── Pydantic models for users ─────────────────────────────────────────────────

class UserBase(SQLModel):
    email: EmailStr = Field(max_length=255)

class UserSignupLogin(UserBase):
    password: str

class UserSignupResponse(UserBase):
    id: uuid.UUID

# This model defines the user object inside the token response
class UserLoginResponse(UserBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    role: str
    is_active: bool

# This is the main response model for the /login endpoint
class AuthTokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserLoginResponse

# ─── Pydantic models for tenants ─────────────────────────────────────────────────

class TenantsBase(SQLModel):
    name: str

class TenantsResponse(TenantsBase):
    id: uuid.UUID
    created_at: datetime.datetime

# ─── Tenants ──────────────────────────────────────────────────────────────────

class Tenants(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tenants_pkey'),
        UniqueConstraint('slug', name='tenants_slug_key')
    )

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

# ─── ORM SQLModel model for users ─────────────────────────────────────────────────

class Users(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='users_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    tenant_id: uuid.UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))
    email: str = Field(sa_column=Column('email', String(320), nullable=False))
    # Argon2 default hash is ~97 chars. 255 provides a safe buffer.
    password_hash: str = Field(sa_column=Column('password_hash', String(255), nullable=False))
    role: str = Field(sa_column=Column('role', String(50), nullable=False, server_default=text("'editor'::character varying")))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

    tenant: 'Tenants' = Relationship(back_populates='users')
    recipes: list['Recipes'] = Relationship(back_populates='users')
